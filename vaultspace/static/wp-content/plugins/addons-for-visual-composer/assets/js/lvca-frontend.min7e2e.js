if(typeof jQuery!="undefined"){(function($){"use strict";$(function(){var LVCA_Frontend={init:function(){this.carousel();this.output_custom_css();this.setup_animations()},isMobile:function(){"use strict";if(/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)){return true}return false},vendor_prefix:function(){var prefix;function prefix(){var styles=window.getComputedStyle(document.documentElement,"");prefix=(Array.prototype.slice.call(styles).join("").match(/-(moz|webkit|ms)-/)||styles.OLink===""&&["","o"])[1];return prefix}prefix();return prefix},output_custom_css:function(){var custom_css=lvca_settings["custom_css"];if(custom_css!==undefined&&custom_css!==""){custom_css='<style type="text/css">'+custom_css+"</style>";$("head").append(custom_css)}},setup_animations:function(){$(".lvca-visible-on-scroll:not(.animated)").css("opacity",0);"function"!=typeof window.lvca_animate_widgets&&(window.lvca_animate_widgets=function(){"undefined"!=typeof $.fn.livemeshWaypoint&&$(".lvca-animate-on-scroll:not(.animated)").livemeshWaypoint(function(){var animateClass=$(this.element).data("animation");$(this.element).addClass("animated "+animateClass).css("opacity",1)},{offset:"85%"})});window.setTimeout(lvca_animate_widgets,500)},carousel:function(){if($().slick===undefined){return}var carousel_elements=$(".lvca-carousel, .lvca-posts-carousel, .lvca-gallery-carousel");carousel_elements.each(function(){var carousel_elem=$(this);var rtl=carousel_elem.attr("dir")==="rtl";var settings=carousel_elem.data("settings");var arrows=settings["arrows"]?true:false;var dots=settings["dots"]?true:false;var autoplay=settings["autoplay"]?true:false;var adaptive_height=settings["adaptive_height"]?true:false;var autoplay_speed=parseInt(settings["autoplay_speed"])||3e3;var animation_speed=parseInt(settings["animation_speed"])||300;var fade="fade"in settings&&settings["fade"]===true;var vertical="vertical"in settings&&settings["vertical"]===true;var pause_on_hover=settings["pause_on_hover"]?true:false;var pause_on_focus="pause_on_focus"in settings&&settings["pause_on_focus"]==true;var display_columns=parseInt(settings["display_columns"])||4;var scroll_columns=parseInt(settings["scroll_columns"])||4;var tablet_width=parseInt(settings["tablet_width"])||800;var tablet_display_columns=parseInt(settings["tablet_display_columns"])||2;var tablet_scroll_columns=parseInt(settings["tablet_scroll_columns"])||2;var mobile_width=parseInt(settings["mobile_width"])||480;var mobile_display_columns=parseInt(settings["mobile_display_columns"])||1;var mobile_scroll_columns=parseInt(settings["mobile_scroll_columns"])||1;carousel_elem.slick({arrows:arrows,dots:dots,infinite:true,autoplay:autoplay,autoplaySpeed:autoplay_speed,speed:animation_speed,fade:false,vertical:vertical,pauseOnHover:pause_on_hover,pauseOnFocus:pause_on_focus,adaptiveHeight:adaptive_height,slidesToShow:display_columns,slidesToScroll:scroll_columns,rtl:rtl,responsive:[{breakpoint:tablet_width,settings:{slidesToShow:tablet_display_columns,slidesToScroll:tablet_scroll_columns}},{breakpoint:mobile_width,settings:{slidesToShow:mobile_display_columns,slidesToScroll:mobile_scroll_columns}}]})})}};LVCA_Frontend.init()})})(jQuery)}