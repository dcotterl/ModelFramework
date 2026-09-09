%% Example: using functions in the model folder
% This script adds the model folder to the MATLAB path, lists its MATLAB
% functions, and displays each function's help text.

clearvars;
clc;

exampleFolder = fileparts(mfilename('fullpath'));
modelFolder = fullfile(exampleFolder, 'model');

if ~isfolder(modelFolder)
	error('The model folder does not exist: %s', modelFolder);
end

addpath(genpath(modelFolder));
cleanupPath = onCleanup(@() rmpath(genpath(modelFolder))); %#ok<NASGU>

% Find functions in the model folder and its subfolders.
modelFiles = dir(fullfile(modelFolder, '**', '*.m'));
modelFiles = modelFiles(~[modelFiles.isdir]);

if isempty(modelFiles)
	fprintf('No MATLAB functions were found in %s.\n', modelFolder);
else
	fprintf('Functions found in %s:\n\n', modelFolder);
	for k = 1:numel(modelFiles)
		[~, functionName] = fileparts(modelFiles(k).name);
		fprintf('%d. %s\n', k, functionName);
		fprintf('   File: %s\n', fullfile(modelFiles(k).folder, modelFiles(k).name));

		% Display the function's first help lines, when available.
		helpText = help(functionName);
		if isempty(helpText)
			fprintf('   No help text available.\n\n');
		else
			helpLines = splitlines(string(helpText));
			fprintf('   %s\n\n', strjoin(helpLines(1:min(5, numel(helpLines))), newline + "   "));
		end
	end
end

%% Calling a model function
modelName = 'average_subsystems';

fprintf('\n--- subsystem_port ---\n');
[inputPorts, outputPorts] = subsystem_port(modelName);
disp(inputPorts);
disp(outputPorts);

fprintf('\n--- continuous_blocks ---\n');
continuousBlocks = continuous_blocks(modelName);
disp(continuousBlocks);

fprintf('\n--- extract_map ---\n');
connections = extract_map(modelName);
disp(connections);

fprintf('\n--- build_subsystems ---\n');
[subsystems, buildInfo] = build_subsystems(modelName);
disp(subsystems);
disp(buildInfo);

%% Inspecting a function before calling it
% which myFunction
% help myFunction
% nargin('myFunction')
% nargout('myFunction')
