const cloudName = 'hbgnmifwf';
const unsignedUploadPreset = 'testing_preset';

var fileSelect = document.getElementById("fileSelect"),
  fileElem = document.getElementById("fileElem");

var addFileSelect = document.getElementById("addFileSelect"),
  addFileElem = document.getElementById("addFileElem");   

if (fileSelect) {
  // Disable navigation on file upload button click - edit
  fileSelect.addEventListener("click", function(e) {
    if (fileElem) {
      fileElem.click();
    }
    e.preventDefault(); 
  }, false);

  // Disable navigation on file upload button click - add
  addFileSelect.addEventListener("click", function(e) {
    if (addFileElem) {
      addFileElem.click();
    }
    e.preventDefault(); 
  }, false);
}

function uploadingButtonStates(fileSelect, saveButton, iconSpan) {

  // disable clicking upload
  fileSelect.addClass('disabled');

  // Disable save button
  saveButton.addClass("disabled");

  // spinner span
  iconSpan.removeClass("glyphicon-camera");
  iconSpan.addClass("glyphicon-repeat");
  iconSpan.addClass('spin');
}

function uploadingFinishedButtonStates(fileSelect, saveButton, iconSpan) {
  // Upload button enabled
  fileSelect.removeClass('disabled');

  // Enable Save button
  saveButton.removeClass("disabled");

  // Remove spinner
  iconSpan.removeClass('spin');
  iconSpan.removeClass("glyphicon-repeat");
  iconSpan.addClass("glyphicon-camera");
}

function thumbnailToGalleryBackgroundImage(galleryElement, url) {
  galleryElement = $(galleryElement);
  galleryElement.css({
    'background-image': 'url(' + url + ')',
    'background-size': 'cover',
    'background-repeat': 'no-repeat',
    'background-position' : 'center center'  
  });
}

// *********** Upload file to Cloudinary from Add ******************** //
function uploadAddFile(file) {
  var url = `https://api.cloudinary.com/v1_1/${cloudName}/upload`;
  var xhr = new XMLHttpRequest();
  var fd = new FormData();
  xhr.open('POST', url, true);
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  xhr.upload.addEventListener("progress", function(e) {

    // console.log(`fileuploadprogress data.loaded: ${e.loaded}, data.total: ${e.total}`);

  uploadingButtonStates(
    $('#addFileSelect'),
    $('button[name="submit"]'),
    $('#addFileSelect span')
    );
  });

  xhr.onreadystatechange = function(e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // File uploaded successfully
      var response = JSON.parse(xhr.responseText);
      var url = response.secure_url;
      var tokens = url.split('/');
      var thumb_tokens = tokens.slice(0);
      var thumb = new Image();
      image_url = tokens.join('/');
      thumb_tokens.splice(6, 0, 't_media_lib_thumb')
      var thumb_src = thumb_tokens.join('/');
      thumb.src = thumb_src;
      document.getElementById("add_image_url").value = image_url;
      
      // Put thumbnail in gallery div
      thumbnailToGalleryBackgroundImage($('#add_gallery'), thumb_src);

      // Reset Buttons
      uploadingFinishedButtonStates(
        $("#addFileSelect"), 
        $('button[name="submit"]'),
        $("#addFileSelect span"));
    }
  };

  fd.append('upload_preset', unsignedUploadPreset);
  fd.append('tags', 'browser_upload'); // Optional - add tag for image admin in Cloudinary
  fd.append('file', file);
  xhr.send(fd);

}


// *********** Upload file to Cloudinary from Edit ******************** //
function uploadFile(file) {
  var url = `https://api.cloudinary.com/v1_1/${cloudName}/upload`;
  var xhr = new XMLHttpRequest();
  var fd = new FormData();
  xhr.open('POST', url, true);
  xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  // Reset the upload progress bar
   // document.getElementById('progress').style.width = 0;
  
  // Update progress (can be used to show progress indicator)
  xhr.upload.addEventListener("progress", function(e) {
    var progress = Math.round((e.loaded * 100.0) / e.total);
    // document.getElementById('progress').style.width = progress + "%";

    uploadingButtonStates(
      $("#fileSelect"), 
      $('button[name="edit-record-save"]'),
      $("#fileSelect span"));
    
    // console.log(`fileuploadprogress data.loaded: ${e.loaded}, data.total: ${e.total}`);
  });

  xhr.onreadystatechange = function(e) {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // File uploaded successfully
      var response = JSON.parse(xhr.responseText);
      var url = response.secure_url;
      var tokens = url.split('/');
      var thumb_tokens = tokens.slice(0);
      var thumb = new Image();
      image_url = tokens.join('/');
      thumb_tokens.splice(6, 0, 't_media_lib_thumb')
      var thumb_src = thumb_tokens.join('/');
      thumb.src = thumb_src;
      document.getElementById("image_url").value = image_url;
      
      // Put thumbnail in gallery div
      thumbnailToGalleryBackgroundImage($('#edit_gallery'), thumb_src);

      // Reset Buttons
      uploadingFinishedButtonStates(
        $("#fileSelect"), 
        $('button[name="edit-record-save"]'),
        $("#fileSelect span"));
    }
  };

  fd.append('upload_preset', unsignedUploadPreset);
  fd.append('tags', 'browser_upload'); // Optional - add tag for image admin in Cloudinary
  fd.append('file', file);
  xhr.send(fd);
}

// *********** Handle selected files ******************** //
var handleFiles = function(files) {
  for (var i = 0; i < files.length; i++) {
    uploadFile(files[i]); // call the function to upload the file
  }
};

var handleAddFiles = function(files) {
  for (var i = 0; i < files.length; i++) {
    uploadAddFile(files[i]); // call the function to upload the file
  }
};