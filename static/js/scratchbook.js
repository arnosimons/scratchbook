$(document).ready(function () {

  document.getElementById("notationButton").click();
  document.getElementById("elementsButton").click();
  document.getElementById("operatorsButton").click();

  var formulaInput = document.getElementById("formulaInput");
  var formulaInput = document.getElementById("formulaInput");

  let tooltipMessage = "Click to audio-visualize!"

  $('.tooltip-code').tooltip({
    trigger: "hover",
    container: 'body',
    title: tooltipMessage
  });

  // Formula
  ////////////////////////////////////////////////////////////////////////////////////

  $(this).on('submit','.home-formula__form',function(e){
    e.preventDefault();
    $.ajax({
      type:'GET',
      url:'/process_formula',
      data:{
        formula:$(".home-formula__input").val()
      },
      success:function(data, textStatus, jqXHR){
        // clear elements
        $( ".home-scratch__message" ).empty();
        $( ".home-scratch__ttm" ).empty();
        $( ".home-scratch__audio" ).empty(); 
        $( ".home-scratch__info" ).empty(); 
        if (data["isWorking"]) {
          let processedFormula = data["processedFormula"].replaceAll('/', '$')
          // create TTM element
          $(".home-scratch__ttm").append(`
            <div class="row overflow-auto">
              <picture>
                <source 
                  srcset="/formulas/${processedFormula}/scratchbook_ttm" 
                  type="image/svg+xml">
                <img class="img" src="alt.png" alt="TTM Plot as svg" />
              </picture>
            </div>
          `)
          // create audio element 
          $(".home-scratch__audio").append(`
          <audio controls>
            <source 
              src="/formulas/${processedFormula}/scratchbook_audio" 
              type="audio/wav">
            Your browser does not support the audio element.
          </audio>
          `)              
          // create info elements
          // analysis
          let groups = ['Elements', 'Combos']
          let groupsHTML = []
          for (let group of groups){
            if (!data["info"][group.toLowerCase()].length == 0){
              let figures = []
              for (let member of data["info"][group.toLowerCase()]){
                figures.push(`
                  <figure 
                      class="figure tooltip-figure" 
                      onclick="document.getElementById('formulaInput').value = '${member}'; formulaButton.click();"
                    >
                    <img src="/formulas/${member}/preview" class="figure-img img-fluid rounded" alt="preview">
                    <figcaption class="figure-caption">
                      ${member}
                    </figcaption>
                  </figure>  
                `)
              }
              let groupHTML = `
                <div class="card border border-0">
                  <div class="home-scratch__info-${group.toLowerCase()} card-body tooltip-card">
                    <p class="card-text">${group}:</p>
                    ${figures.map(i => i).join(" ")}
                  </div>
                </div>`
              groupsHTML.push(groupHTML)
            }
          }
          $(".home-scratch__info").append(`
            <div class="col">
              <div class="card border mb-3" style="min-width: 9rem;">
                <div class="card-header">
                  <a 
                    class="btn cardHeader" 
                    data-bs-toggle="collapse" 
                    aria-expanded="true"
                    href=".home-scratch__info-analysis" 
                    style="width: 100%">
                    &#128270; Analysis
                  </a>
                </div>
              </div>
              <div class="home-scratch__info-analysis collapse show">
                <div class="card-body">
                  <p class="card-text">
                    Your scratch has ${data["info"]["F"]} ${data["info"]["F"] == 1 ? 'click' : 'clicks'} and makes ${data["info"]["sounds"]} ${data["info"]["sounds"] == 1 ? 'sound' : 'sounds'}
                  </p>
                  <p class="card-text">
                    It contains ${data["info"]["variations"] == 1 ? '(variations of) ' : ''} the following generic components:                      
                  </p>
                  <div class="card-group">
                    ${groupsHTML.map(i => i).join(" ")}
                  </div
                </div>
              </div>
            </div>
          `);
          $('.tooltip-figure').tooltip({
            trigger: "hover",
            container: '.tooltip-card',
            title:tooltipMessage,
          });
          // tutorials
          if (!data["tutorials"].length == 0){
            buttons = []
            items = []
            for (let [index, youtubeID] of data["tutorials"].entries()){
              buttons.push(
                `<button type="button" data-bs-target="tutorialCarousel" data-bs-slide-to="${index}" class="${index == 0 ? 'active' : ''}" aria-current="true" aria-label="Slide ${ index + 1 }"></button>`
              )
              items.push(`
                <div class="carousel-item ${index == 0 ? 'active' : '' } ratio ratio-4x3">
                  <iframe 
                    src="https://www.youtube.com/embed/${ youtubeID }" 
                    title="YouTube video player" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen>
                  </iframe> 
                </div>
              `)
            }
            $(".home-scratch__info").append(`
              <div class="col">
                <div class="card border mb-3" style="min-width: 9rem;">
                  <div class="card-header">
                    <a 
                      class="btn cardHeader" 
                      data-bs-toggle="collapse" 
                      aria-expanded="true"
                      href=".home-scratch__info-tutorials" 
                      title="Learn how to speak scratch algebra"
                      style="width: 100%">
                      &#128250; Related Tutorials            
                    </a>
                  </div>
                  <div class="home-scratch__info-tutorials collapse show">
                    <div class="card-body">
                      <div id="tutorialCarousel" class="carousel slide" data-bs-ride="false">
                        <div class="carousel-indicators">
                          ${buttons.map(i => i).join(" ")}
                        </div>
                        <div class="carousel-inner">
                          ${items.map(i => i).join(" ")}
                        </div>
                        <button class="carousel-control-prev" type="button" data-bs-target="#tutorialCarousel" data-bs-slide="prev">
                          <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                          <span class="visually-hidden">Previous</span>
                        </button>
                        <button class="carousel-control-next" type="button" data-bs-target="#tutorialCarousel" data-bs-slide="next">
                          <span class="carousel-control-next-icon" aria-hidden="true"></span>
                          <span class="visually-hidden">Next</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            `)
          }
        }
        else {
          if (!data["isEmpty"]) {
            $('<p/>', {
              class:"text-danger",
            }).append(data["message"]).appendTo(".home-scratch__message");
          }
        }
      }
    })
  });
  
  // Library
  ////////////////////////////////////////////////////////////////////////////////////
  
  var table = $('#library').DataTable({
    serverSide: true,
    ajax: "/library/data",
    columns: [
      {data:"Preview", title: "Preview"}, // 0
      {data:"Name(s)", title: "Name(s)"}, // 1
      {data:"sounds", title: "Sounds"}, // 2
      {data:"F", title: "Clicks"}, // 3
      {data:"variations", title: "ExLog"}, // 4
      {data:"Formula", title: "Formula"}, // 5
      {data:"libraries", title: "libraries", visible: false}, // 6
    ],
    order: [
      [ 0, "asc" ], 
    ],
    "searching": true,
    "lengthChange": true,
    scrollY: '50vh',
    scrollCollapse: true,
    fixedHeader: {
      header: true,
    },
    "initComplete": function(settings){
      // Tooltips for clicking Previews and Names
      $('#library tbody tr').each(function () {
        var tr = $(this);
        td1 = tr.find("td:eq(0)");
        td1.attr('title', tooltipMessage);

        td2 = tr.find("td:eq(1)");
        td2.attr('title', tooltipMessage);
      });
      /* Style header tooltips */
      $('#library [title]').tooltip({
        trigger: "hover",
        "container": 'body',
      });
      // Get name when clicking on rows
      $('#library').on('click', 'td', function () {
        var cell = table.cell( this ).data();
        var colindx = table.column( this ).index();
        if (colindx == 0 || colindx == 1) {
          var row = table.row( this ).data();
          var names = row["Name(s)"];
          names = names.split(",");
          formulaInput.value = names[0];
          formulaButton.click();
        }; 
      });
    },
  });
  // Functions for row-filtering switches  
  function activeLibs() { // return all currently switched libs
    let libraries = [];
    for (let lib of ["CORE", "ELEMENTS", "TEARS", "ORBITS", "COMBOS"]) {
      if (document.getElementById(lib).checked) {
          libraries.push(lib)
        }
    }
    return libraries.join(" ")
  };
  for (let lib of ["CORE", "ELEMENTS", "TEARS", "ORBITS", "COMBOS"]) { // make function for each lib switch
    $("#" + lib).change(function() {
      table.column( 6 ).search( activeLibs() ).draw();
    });
  }
  table.column( 6 ).search( activeLibs() ).draw(); // ensures that DEFAULT lib (whatever is set in html) is filtered

  });