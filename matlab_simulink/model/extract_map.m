function connections = extract_map(modelName)
%EXTRACT_MAP Map Goto/From tags to the blocks that generate/consume signals.
%   CONNECTIONS = EXTRACT_MAP(MODELNAME) scans the top level of MODELNAME
%   for Goto and From blocks and, for each tag, resolves the block feeding
%   the Goto block (Output) and the block(s) fed by the matching From
%   block(s) (Inputs), returning a table.
%
%   Example:
%       connections = extract_map('average_subsystems');
%       disp(connections);
arguments (Input)
    modelName (1,:) char
end

arguments (Output)
    connections table
end

wasLoaded = bdIsLoaded(modelName);
if ~wasLoaded
    load_system(modelName);
end

gotoBlocks = find_system(modelName, 'SearchDepth', 1, 'BlockType', 'Goto');
fromBlocks = find_system(modelName, 'SearchDepth', 1, 'BlockType', 'From');

tags = containers.Map('KeyType', 'char', 'ValueType', 'any');

for k = 1:numel(gotoBlocks)
    blk = gotoBlocks{k};
    tag = get_param(blk, 'GotoTag');
    entry = getOrCreateEntry(tags, tag);

    lineHandles = get_param(blk, 'LineHandles');
    inportLine = lineHandles.Inport(1);
    if inportLine > 0
        srcHandle = get_param(inportLine, 'SrcBlockHandle');
        entry.Output = string(getfullname(srcHandle));
    end
    tags(tag) = entry;
end

for k = 1:numel(fromBlocks)
    blk = fromBlocks{k};
    tag = get_param(blk, 'GotoTag');
    entry = getOrCreateEntry(tags, tag);

    lineHandles = get_param(blk, 'LineHandles');
    outportLine = lineHandles.Outport(1);
    if outportLine > 0
        dstHandles = get_param(outportLine, 'DstBlockHandle');
        for d = 1:numel(dstHandles)
            entry.Inputs(end+1) = string(getfullname(dstHandles(d)));
        end
    end
    tags(tag) = entry;
end

tagKeys = keys(tags);
rows = cell(numel(tagKeys), 3);
for k = 1:numel(tagKeys)
    entry = tags(tagKeys{k});
    rows{k,1} = entry.Tag;
    rows{k,2} = entry.Output;
    rows{k,3} = {entry.Inputs};
end

connections = cell2table(rows, 'VariableNames', {'Tag', 'Output', 'Inputs'});

if ~wasLoaded
    close_system(modelName, 0);
end
end

function entry = getOrCreateEntry(tags, tag)
% Return the existing map entry for TAG, creating a blank one if needed.
if isKey(tags, tag)
    entry = tags(tag);
else
    entry = struct('Tag', string(tag), 'Output', string(missing), 'Inputs', string.empty(1,0));
    tags(tag) = entry;
end
end
