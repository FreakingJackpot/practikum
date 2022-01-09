$('.open-popup').click(function (e) {
  e.preventDefault();
  $('.popup').fadeIn(800);
  $('html').addClass('no-scroll');
});

$('.close-popup').click(function () {
  $('.popup').fadeOut(800);
  $('html').removeClass('no-scroll');
});

$('.slider').slick({
  dots: true,
  arrows: false,
  fade: true,
  autoplay: true,
  interval: 7000,
});
$('.slider__sale').slick({
  autoplay: true,
  prevArrow:'<button type = "button" class = "slider__sale-arrow slider__sale-arrowleft"><img src="images/arrow-left.svg" alt="arrow left"></button>',
  nextArrow:'<button type = "button" class = "slider__sale-arrow slider__sale-arrowright"><img src="images/arrow-right.svg" alt="arrow right"></button>',
});