function [inputPorts,outputPorts] = subsystem_port(modelName)
%SUBSYSTEM_PORT List input/output ports of first-level subsystems.
%   [IN,OUT] = SUBSYSTEM_PORT(MODELNAME) scans the subsystems located one
%   level below the top of MODELNAME and returns two tables describing the
%   Inport and Outport blocks found inside each subsystem.
%
%   Example:
%       [inputPorts, outputPorts] = subsystem_port('simple_subsystems');
%       disp(inputPorts);
%       disp(outputPorts);
arguments (Input)
    modelName (1,:) char
end

arguments (Output)
    inputPorts table
    outputPorts table
end

wasLoaded = bdIsLoaded(modelName);
if ~wasLoaded
    load_system(modelName);
end

subsystems = find_system(modelName, ...
    'SearchDepth', 1, ...
    'LookUnderMasks', 'all', ...
    'BlockType', 'SubSystem');

inRows  = cell(0,4);
outRows = cell(0,4);

for k = 1:numel(subsystems)
    subsys = subsystems{k};
    subsysName = get_param(subsys, 'Name');

    inBlocks = find_system(subsys, ...
        'SearchDepth', 1, ...
        'LookUnderMasks', 'all', ...
        'BlockType', 'Inport');
    for p = 1:numel(inBlocks)
        inRows(end+1,:) = { string(subsysName), ...
            string(subsys), ...
            string(get_param(inBlocks{p}, 'Name')), ...
            str2double(get_param(inBlocks{p}, 'Port')) }; %#ok<AGROW>
    end

    outBlocks = find_system(subsys, ...
        'SearchDepth', 1, ...
        'LookUnderMasks', 'all', ...
        'BlockType', 'Outport');
    for p = 1:numel(outBlocks)
        outRows(end+1,:) = { string(subsysName), ...
            string(subsys), ...
            string(get_param(outBlocks{p}, 'Name')), ...
            str2double(get_param(outBlocks{p}, 'Port')) }; %#ok<AGROW>
    end
end

varNames = {'Subsystem','SubsystemPath','PortName','PortNumber'};
if isempty(inRows)
    inputPorts = cell2table(cell(0,4), 'VariableNames', varNames);
else
    inputPorts = cell2table(inRows, 'VariableNames', varNames);
end
if isempty(outRows)
    outputPorts = cell2table(cell(0,4), 'VariableNames', varNames);
else
    outputPorts = cell2table(outRows, 'VariableNames', varNames);
end

if ~wasLoaded
    close_system(modelName, 0);
end
end