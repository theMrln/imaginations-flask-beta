local mediabag = require "pandoc.mediabag"
local path = require "pandoc.path"
local system = require "pandoc.system"
local thisFile = path.filename("the/path/to/filename.ext") -- the filename without the whole path
local outputfile = PANDOC_STATE.output_file:gsub("%.md", "") -- markdown file without file extension
local thisDirectory = system.get_working_directory() -- the path to the script directory
-- the regex below could probably be substituted by something cleaner
local function prefixName(s)
    return s:gsub("([^/]*)$", outputfile .. "_%1")
end

-- the following changes the default output by removing the media/ subdir
for fp, mt, contents in mediabag.items() do
    local fpnew = prefixName(fp)
    -- print(fpnew)
    fpnew = fpnew:gsub("media/markdown/", "")
    pandoc.mediabag.insert(fpnew, mt, contents)
    mediabag.delete(fp)
end
-- modify the image links to reflect the changes to the mediabag above
function Image(img)
    local thisImage = img.src:gsub("media/", "") -- the media subdir is removed from the filename
    thisImage = prefixName(thisImage)
    thisImage = path.filename(thisImage)
    local thisRelevantDirectory = outputfile:gsub("%.md", "") -- the extension is removed from markdown file
    thisRelevantDirectory = thisRelevantDirectory:gsub("markdown/", "")
    img.src = "../static/media/" .. thisRelevantDirectory .. "-media/" .. thisImage
    -- the relative path to the moved image (above)  is constructed
    -- img.src = thisDirectory .. "/" .. thisRelevantDirectory .. "/" .. thisImage
    img.attr = "" -- delete the width parameters
    return img
end
