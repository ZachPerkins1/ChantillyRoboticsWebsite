$(document).ready(function(){
  if($("#about-first").length!=0){ //So it only runs on the one page
    $(".subtitle").click(function(){
      $(this).next().slideToggle(300); //Goes inside the contentbox, finds all p's, get's the second (index 1)
    });
  }
  //Note: The load functions will not load local files in Chrome, Internet Explorer, or Edge.
  //They should work when the files are remote hosted though.
  //If you want to see the header and footer loaded on local, use Firefox.
  $("#header").load("header.html #header-body");
  $("#footer").load("footer.html #footer-body");
});
