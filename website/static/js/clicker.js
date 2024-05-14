$('.clicker-content').hide();

$('.clicker').click(function(){
    $(this).nextUntil('.clicker').slideToggle('fast').toggleClass('active');
    $(this).find('.clicker-arrow').toggleClass('rotate-down');
  });

document.getElementById('demo').innerHTML = "This is changed by js file"