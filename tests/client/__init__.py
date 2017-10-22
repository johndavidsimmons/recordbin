# remove any UI screenshots from old test runs
import os

screenshots_path = 'tests/client/screenshots'
# create directory if it doesn't already exist
if not os.path.exists(screenshots_path):
    os.makedirs(screenshots_path)

# get all files in path
fileList = os.listdir(screenshots_path)
for filename in fileList:
    # formulate correct path for file
    item = os.path.join(screenshots_path, filename)
    # remove item if it is a file
    if os.path.isfile(item):
        os.remove(item)
