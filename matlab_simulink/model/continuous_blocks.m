function continuousBlocks = continuous_blocks(modelName)
% SUBSYSTEM Identify all continuous blocks present in a given model.
%
%   continuousBlocks = subsystem(modelName) loads (if necessary) the
%   model specified by modelName, scans all blocks in the model
%   hierarchy, and returns a list of blocks that have continuous sample
%   time (SampleTime == 0 or ContStateInfo indicates continuous states).
%
%   Input:
%       modelName - name of the Simulink model (char/string), with or
%                   without .slx/.mdl extension
%
%   Output:
%       continuousBlocks - table with columns:
%           BlockPath   - full path of the block
%           BlockType   - type of the block
%           SampleTime  - sample time of the block

    if nargin < 1 || isempty(modelName)
        error('subsystem:invalidInput', 'A model name must be provided.');
    end

    % Strip extension if provided
    [~, modelName, ~] = fileparts(modelName);

    % Load the model if it is not already open
    if ~bdIsLoaded(modelName)
        load_system(modelName);
        closeAfter = true;
    else
        closeAfter = false;
    end

    try
        % Ensure the model is compiled to get accurate sample time info
        eval([modelName '([], [], [], ''compile'');']);
        compiled = true;
    catch
        compiled = false;
    end

    try
        % Get all blocks in the model hierarchy
        allBlocks = find_system(modelName, 'LookUnderMasks', 'all', ...
            'FollowLinks', 'on');

        blockPaths = {};
        blockTypes = {};
        sampleTimes = {};

        for i = 1:numel(allBlocks)
            blockPath = allBlocks{i};

            % Skip the model root itself
            if strcmp(blockPath, modelName)
                continue;
            end

            blockType = get_param(blockPath, 'BlockType');

            isContinuous = false;
            sampleTimeVal = [];

            if compiled
                try
                    st = get_param(blockPath, 'CompiledSampleTime');
                    sampleTimeVal = st;
                    % Continuous sample time is represented as [0 0] or [0 1]
                    if isnumeric(st) && ~isempty(st) && st(1) == 0
                        isContinuous = true;
                    end
                catch
                    % Some blocks (e.g., virtual/subsystem blocks) may not
                    % have a CompiledSampleTime parameter
                end
            end

            % Fallback: check for blocks known to introduce continuous
            % states (e.g., Integrator, TransferFcn, StateSpace, etc.)
            if ~isContinuous
                continuousBlockTypes = {'Integrator', 'TransferFcn', ...
                    'StateSpace', 'ZeroPole', 'Derivative', ...
                    'TransportDelay', 'VariableTransportDelay'};
                if any(strcmp(blockType, continuousBlockTypes))
                    isContinuous = true;
                end
            end

            if isContinuous
                blockPaths{end+1, 1} = blockPath; %#ok<AGROW>
                blockTypes{end+1, 1} = blockType; %#ok<AGROW>
                sampleTimes{end+1, 1} = sampleTimeVal; %#ok<AGROW>
            end
        end

        continuousBlocks = table(blockPaths, blockTypes, sampleTimes, ...
            'VariableNames', {'BlockPath', 'BlockType', 'SampleTime'});

    catch ME
        if compiled
            eval([modelName '([], [], [], ''term'');']);
        end
        if closeAfter
            close_system(modelName, 0);
        end
        rethrow(ME);
    end

    if compiled
        eval([modelName '([], [], [], ''term'');']);
    end

    if closeAfter
        close_system(modelName, 0);
    end

    fprintf('Found %d continuous block(s) in model "%s".\n', ...
        height(continuousBlocks), modelName);

end

% Example usage:
%
%   continuousBlocks = subsystem('simple_subsystems');
%   disp(continuousBlocks);
%
% This will load (if necessary) the model "simple_subsystems.slx",
% scan its block hierarchy, and return a table listing all blocks
% that have continuous sample time (e.g., Integrator, TransferFcn,
% StateSpace, etc.), along with their block paths, types, and sample
% times.
