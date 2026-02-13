window.onload = function () {
  try {
    loadSections(jQuery);
  } catch (err) {
    if (err.message.includes("null")) {
      setTimeout(function () {
        console.log("got put in timeout");
        loadSections(jQuery);
      }, 200);
    } else {
      console.log(err);
      if (!err.message.includes("marked")) {
        jQuery(".card").before(jQuery("<h3 id='topnav'>").text(err));
        jQuery("h3 #topnav").append(
          jQuery("<p>").text("Please raise an issue in the GitHub repository."),
        );
      }
    }
  }
};

function loadSections($) {
  let sections = ["topnav", "footer"];
  $(`#${sections[0]}`).load(`load.html #${sections[0]}`, function () {
    $(`#${sections[1]}`).load(`load.html #${sections[1]}`);
  });
  if (window.location.href.includes("about")) {
    $("#about").load("../../README.md");
    setTimeout(function () {
      let mdText = $("#about").html();
      $("#about").html(marked.parse(mdText));
    }, 200);
    $("#about").html(marked.parse([0].innerHTML));
  } else if (window.location.href.includes("index")) {
    console.log("inside index");
    addListeners(jQuery);
    authref(jQuery);
  }
}

function addListeners($) {
  $(".card").on("change", "#manuscript", () => {
    let file = $("#manuscript").files[0]; // There's something wrong with this line
    console.log(file);
    $("#filename").text = file ? file.name : "No File Selected";
  });

  $(".card").on("click", "#add-author", () => {
    $("#authors").append(
      $("<div class='author-row'>").html(`
          <label>
            <span class="author-label">Author</span>
            <input name="authors" type="text" placeholder="Last, First" required />
          </label>
          <label>
            <span class="author-label">Affiliation</span>
            <input
              name="author_affiliations"
              type="text"
              placeholder="Department, Institution"
              required
            />
          </label>`),
    ); // <button type="button" class="remove-author" aria-label="Remove Author">Remove</button>
    authref(jQuery);
  });
  $(".card").on("click", ".remove-author", () => {
    // $(".remove-author").parent(".author-row").remove(); ** couldn't get this to work **
    $(".author-row").remove(); // temporarily until I get it fixed (it's a remove all for now)
    authref(jQuery);
  });

  $(".submit").on("change", (e) => {
    let upload = new Upload($("#manuscript").files[0]);
    upload.doUpload()
  });
}

// Upload Class
// https://stackoverflow.com/questions/2320069/jquery-ajax-file-upload
let Upload = (file) => {
  this.file = file;
};
Upload.getType = () => {
  return this.file.type;
};
Upload.getSize = () => {
  return this.file.size;
};
Upload.getName = () => {
  return this.file.name;
};
Upload.doUpload = () => {
  let that = this;
  let formData = new FormData();
  formData
    .append("file", this.file, this.getName())
    .append("upload_file", true);

  $.ajax({
    type: "POST",
    url: "script",
    xhr: () => {
      let myXhr = $.ajaxSettings.xhr();
      if (myXhr.upload)
        myXhr.upload.addEventListener("progress", that.progressHandling, false);
      return myXhr;
    },
    success: () => {
      // Do the python thing
    },
    error: () => {
      $("#manuscript").append(
        $("<p>").text("There was an error, please reload and try again."),
      );
    },
    axync: true,
    data: formData,
    cahche: false,
    contentType: false,
    processData: false,
    timeout: 60000,
  });
};
Upload.progressHandling = (event) => {
  let position = event.loaded || event.position;
  let total = event.total;
  $("#manuscript").append(
    $("<p>").text(`Progress: ${Math.ceil((position / total) * 100)}%`),
  );
};

function refreshAuthors($) {
  // I made a function that works (this threw errors)
  const authors = document.getElementById("authors");
  const rows = authors.querySelectorAll(".author-row");
  rows.forEach((row, index) => {
    const labels = row.querySelectorAll(".author-label");
    if (labels[0]) labels[0].textContent = `Author ${index + 1}`;
    if (labels[1]) labels[1].textContent = `Affiliation ${index + 1}`;
    const remove = row.querySelector(".remove-author"); // But what is this section for
    const disabled = rows.length === 1;
    remove.disabled = disabled;
    remove.style.visibility = disabled ? "hidden" : "visible";
  });
}

function authref($) {
  let authors = $(".author-row")
    .map(function () {
      return this;
    })
    .get();
  let removeAuths = $(".remove-author").map(function () {
    return this;
  });
  let labels = $(".author-label")
    .map(function () {
      return this;
    })
    .get();
  for (let i = 0; i < labels.length; i++) {
    if (i % 2 == 0) labels[i].textContent = `Author ${i / 2 + 1}`;
    else labels[i].textContent = `Affiliation ${(i - 1) / 2 + 1}`;
  }
  for (let j = 0; j < authors.length; j++) {
    // Setup for removing only one author at a time (match IDs)
    $(authors[j]).attr("id", `auth-${j}`);
    $(removeAuths[j]).attr("id", `rem-${j}`);
  }
}
