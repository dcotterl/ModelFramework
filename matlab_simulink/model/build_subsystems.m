function [subsystems, buildInfo] = build_subsystems(modelName, modelParams)
%BUILD_SUBSYSTEMS Build every top-level subsystem with Simulink Coder.
%   [SUBSYSTEMS, BUILDINFO] = BUILD_SUBSYSTEMS(MODELNAME, MODELPARAMS)
%   loads MODELNAME, finds the subsystems exactly one level below the model
%   root, applies the configuration parameters given in the MODELPARAMS
%   struct (field name = parameter name, value = parameter value) and
%   generates code for each subsystem using slbuild.
%
%   Example with model configuration parameters:
%       params = struct('SystemTargetFile', 'veristand.tlc');
%       [subsystems, buildInfo] = build_subsystems('simple_subsystems', params);
arguments (Input)
    modelName (1,:) char
    modelParams struct = struct()
end

arguments (Output)
    subsystems  cell
    buildInfo   struct
end

% Make sure the model is in memory.
if ~bdIsLoaded(modelName)
    load_system(modelName);
end

% Apply the model parameters coming from the caller.
paramNames = fieldnames(modelParams);
for k = 1:numel(paramNames)
    set_param(modelName, paramNames{k}, modelParams.(paramNames{k}));
end

% Only the subsystems one level down from the top level.
subsystems = find_system(modelName, ...
    'SearchDepth', 1, ...
    'LookUnderMasks', 'all', ...
    'BlockType', 'SubSystem');

buildInfo = struct('Subsystem', {}, 'Status', {}, 'Message', {});

for k = 1:numel(subsystems)
    blk = subsystems{k};
    info = struct('Subsystem', blk, 'Status', 'built', 'Message', '');
    try
        % Subsystem must be atomic for slbuild to treat it as its own build target.
        set_param(blk, 'TreatAsAtomicUnit', 'on');
        slbuild(blk);
    catch buildErr
        info.Status  = 'failed';
        info.Message = buildErr.message;
        warning('build_subsystems:BuildFailed', ...
            'Failed to build "%s": %s', blk, buildErr.message);
    end
    buildInfo(end+1) = info; %#ok<AGROW>
end
end