const cloudName = 'hbgnmifwf';
const unsignedUploadPreset = 'testing_preset';

var fileSelect = document.getElementById("fileSelect"),
  fileElem = document.getElementById("fileElem");

fileSelect.addEventListener("click", function(e) {
  if (fileElem) {
    fileElem.click();
  }
  e.preventDefault(); // prevent navigation to "#"
}, false); 

// *********** Upload file to Cloudinary ******************** //
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

    // disable clicking upload
    $("#fileSelect").addClass('disabled');

    // spinner
    $("#fileSelect span").removeClass("glyphicon-camera");
    $("#fileSelect span").addClass("glyphicon-repeat");
    $('#fileSelect span').attr('id', 'spin');
    
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
      $("#gallery").css({
        'background-image': 'url(' + thumb_src + ')',
        'background-size': 'cover',
        'background-repeat': 'no-repeat',
        'background-position' : 'center center'  
      });
      $("#fileSelect").removeClass('disabled');
      $('#fileSelect span').attr('id', '');
      $("#fileSelect span").removeClass("glyphicon-repeat");
      $("#fileSelect span").addClass("glyphicon-camera");
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