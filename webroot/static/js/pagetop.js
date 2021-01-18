/*
 * <head>
 *   :
 *   <link rel="stylesheet" href="/bootstrap/css/bootstrap.min.css">
 *   <link rel="stylesheet" href="/fontawesome/css/all.css">
 *   <link rel="stylesheet" href="/ytnet/css/fa-pagetop.css">
 *   :
 * </head>
 * <body>
 *   :
 *   </footer>
 *   <p class="pagetop"><a href="#wrap"><i class="fa fa-chevron-up"></i></a></p>
 *   :
 *   <script src="/jquery/jquery-3.5.1.min.js"></script>
 *   <script src="/bootstrap/js/bootstrap.bundle.js"></script>
 *   <script src="/ytnet/js/fa-pagetop.js"></script>
 *   :
 * </body>
 */
$(document).ready(function() {
    var pagetop = $('.pagetop');
    $(window).scroll(function () {
        if ($(this).scrollTop() > 5) {
            pagetop.fadeIn();
        } else {
            pagetop.fadeOut();
        }
    });
    pagetop.click(function () {
        $('body, html').animate({ scrollTop: 0 }, 500);
        return false;
    });
});
