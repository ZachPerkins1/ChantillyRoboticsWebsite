$(document).ready(function(){
  //Note: The load functions will not load local files in Chrome, Internet Explorer, or Edge.
  //They should work when the files are remote hosted though.
  //If you want to see the header and footer loaded on local, use Firefox.
  $("#header").load("header.html", function() {
    //Returns the rightmost file/directory name sans page anchor and queries
    var page = location.href.split("/").slice(-1)[0].split(/#|\?/, 1)[0];
    if(page == "" || page == "612-Website"){ //Second case is if the page loaded is .../612-Website with no ending slash, just in case
      $("#navbar a[href='index.html']").addClass("active"); //Finds anchor element with reference to index.html
      return false; //No need to check the rest
    }
    $("#navbar a").each(function() {
      if($(this).attr("href") == page) {
        $(this).addClass("active");
        return false;
      }
    });
  });
  $("#footer").load("footer.html");
  //put mobile-specific (or desktop-specific) code here
  function onMobileChange(query) {
    //mobile
    if(query.matches) {
      $(".subtitle").next().hide();
      $(".subtitle").click(function() {
        $(this).next().slideToggle(300);
      });
      $(".desktop-only").hide(); //elements we want only on desktop
      $(".mobile-only").show();
    //desktop
    } else {
      $(".subtitle").next().show();
      $(".subtitle").off("click");
      $(".desktop-only").show();
      $(".mobile-only").hide(); //elements we want only on mobile
    }
  }
  var media = window.matchMedia("screen and (max-width: 1000px)");
  media.addListener(onMobileChange);
  onMobileChange(media);
  //end mobile/desktop specific code
});
