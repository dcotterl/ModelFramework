%% Example: using functions in the utilities folder
% This script adds the model and utilities folders to the MATLAB path,
% lists the MATLAB utilities, and displays each utility's help text.

clearvars;
clc;

exampleFolder = fileparts(mfilename('fullpath'));
modelFolder = fullfile(exampleFolder, 'model');
utilitiesFolder = fullfile(exampleFolder, 'utilities');

if ~isfolder(modelFolder)
	error('The model folder does not exist: %s', modelFolder);
end
if ~isfolder(utilitiesFolder)
	error('The utilities folder does not exist: %s', utilitiesFolder);
end

addpath(genpath(modelFolder));
addpath(genpath(utilitiesFolder));
cleanupPath = onCleanup(@() cleanupExamplePath(modelFolder, utilitiesFolder)); %#ok<NASGU>

% Find utilities in the utilities folder and its subfolders.
utilityFiles = dir(fullfile(utilitiesFolder, '**', '*.m'));
utilityFiles = utilityFiles(~[utilityFiles.isdir]);

if isempty(utilityFiles)
	fprintf('No MATLAB utilities were found in %s.\n', utilitiesFolder);
else
	fprintf('Utilities found in %s:\n\n', utilitiesFolder);
	for k = 1:numel(utilityFiles)
		[~, functionName] = fileparts(utilityFiles(k).name);
		fprintf('%d. %s\n', k, functionName);
		fprintf('   File: %s\n', fullfile(utilityFiles(k).folder, utilityFiles(k).name));

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

function cleanupExamplePath(modelFolder, utilitiesFolder)
rmpath(genpath(modelFolder));
rmpath(genpath(utilitiesFolder));
end
