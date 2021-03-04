var move_footer_nav = 1;

///////////////////////////////////

var isIE11 = !!(navigator.userAgent.match(/Trident/) && navigator.userAgent.match(/rv[ :]11/));

var url = window.location.href;

var col_pos = new Array();
var col_items = new Array();
var col_heights = new Array();

function getCookie(c_name){
    if (document.cookie.length > 0){
        c_start = document.cookie.indexOf(c_name + "=");
        if (c_start != -1){
            c_start = c_start + c_name.length + 1;
            c_end = document.cookie.indexOf(";", c_start);
            if (c_end == -1) c_end = document.cookie.length;
            return unescape(document.cookie.substring(c_start,c_end));
        }
    }
    return "";
}

$(function () {
    $.ajaxSetup({
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    });
});

$.fn.equalizeHeights = function () {
	return this.height(
		Math.max.apply(this, $(this).map(function (i, e) {
			return $(e).height();
		}).get()
		));
};

var fade_intervall = 4000;
var fade_dauer = 1000;
var fade_dauer_klick = 150;

function BildFader(ind_neu, dauer) {

	var alt = $('#slideshow div.slidebox.obersteebene');

	if (typeof (ind_neu) == "undefined") {
		var neu = alt.next('.slidebox').length ? alt.next('.slidebox') : $('#slideshow div.slidebox:first');
		ind_neu = neu.index();
	}
	else var neu = $('#slideshow div.slidebox').eq(ind_neu * 1);

	if (typeof (dauer) == "undefined")
		dauer = fade_dauer;
	else
		dauer = dauer * 1; 

	alt.addClass('mittlereebene').removeClass('obersteebene');

	neu.fadeOut(0, function () {
		neu.addClass('obersteebene').fadeIn(dauer, function () {
			alt.removeClass('mittlereebene');
		});
		
		$('div#slideshow-seitenanzeige span')
			.removeClass('aktiv')
			.eq(ind_neu)
			.addClass('aktiv');
	});
}

$(document).ready(function () {

	if (move_footer_nav) {
		$('footer ul.navlist').not('#nav_social').children('li').clone().attr('id', '').addClass('fnav').appendTo('#nav1 ul.navlist:first');
		$('footer ul.navlist').not('#nav_social').addClass('opt');
	}

	/* Mobil Menü Erweiterungen */
	$('header:first .inner').prepend('<div id="menubutton"><div id="balken"><div id="mb1" class="menueBalken mb1"></div><div id="mb2" class="menueBalken mb2"></div><div id="mb3" class="menueBalken mb3"></div></div></div>');

	$('#menubutton').click(function () {
		var scrollTop = $(window).scrollTop();
		$('html, body').animate({ scrollTop: 0 }, 300);

		if (scrollTop > 0 || !$("#nav1 ul.navlist").hasClass("show")) {
			$("#nav1 ul.navlist").addClass("show");

			$("#menubutton .mb1, #menubutton .mb2, #menubutton .mb3").addClass("active");
			$("#balken").addClass("balken");
		} else {
			$("#nav1 ul.navlist").removeClass("show");
			$("#menubutton .mb1, #menubutton .mb2, #menubutton .mb3").removeClass("active");
			$("#balken").removeClass("balken");
		}

		if ($('#nav1').hasClass('open')) {
			$('#nav1').removeClass('open');
		}
		else {
			$('#nav1').addClass('open');
		}
	});

	window.onload = function () { scrollcheck(); };

	window.onresize = function () { scrollcheck(); };

	var timer_scroll;
	$(window).scroll(function () {
		if (timer_scroll) {
			window.clearTimeout(timer_scroll);
		}
		timer_scroll = window.setTimeout(function () { scrollcheck(); }, 10);
	});

	function scrollcheck() {
		if ($(window).scrollTop() > 100) {
			$('html').addClass('menu_altern');
		}
		else $('html').removeClass('menu_altern');
	}

	if ($('#slideshow div.slidebox').length > 1) {
		$('#slideshow').append('<div id="slideshow-seitenanzeige"></div>').append('<div id="slideshow-buttons"><div id="slider-bt-prev"></div><div id="slider-bt-next"></div></div>');
		$('#slideshow .slidebox').each(function () {
			
			$('div#slideshow-seitenanzeige')
				.append('<span></span>')
				.children('span:last')
				.click(function () {
					BildFader($(this).index(), fade_dauer_klick);
				});
		});

		$('div#slideshow-seitenanzeige span').eq($('#slideshow div.slidebox.obersteebene').index()).addClass('aktiv');

		$('#slideshow #slideshow-buttons div#slider-bt-next').click(function (event) {
			event.preventDefault();
			var alt = $('#slideshow div.slidebox.obersteebene');
			var neu = alt.next('.slidebox').length ? alt.next('.slidebox') : $('#slideshow div.slidebox:first');
			BildFader(neu.index(), fade_dauer_klick);
		});

		$('#slideshow #slideshow-buttons div#slider-bt-prev').click(function (event) {
			event.preventDefault();
			var alt = $('#slideshow div.slidebox.obersteebene');
			var neu = alt.prev('.slidebox').length ? alt.prev('.slidebox') : $('#slideshow div.slidebox:last');
			BildFader(neu.index(), fade_dauer_klick);
		});

		var fadeit = setInterval("BildFader()", fade_intervall);

		$('#slideshow').hover(function () {
			if ($('#navbutton:visible').length === 0) {
				window.clearInterval(fadeit);
			}
		}, function () {
			window.clearInterval(fadeit);
			fadeit = setInterval("BildFader()", fade_intervall);
		});
	}
});//ENDE document ready