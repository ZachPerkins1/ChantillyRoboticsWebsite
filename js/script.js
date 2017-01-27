$(document).ready(function(){
  $(".contentbox").click(function(){
    $(this).find("p").eq(1).slideToggle(300);
  });
});
