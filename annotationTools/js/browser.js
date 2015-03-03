// This file contains functions for interacting with the browser type.

var bname;
var bversion;

function GetBrowserInfo() {
 /**
	alert(navigator.appCodeName);
   alert(navigator.appName);
   alert(navigator.appVersion);
   alert(navigator.cookieEnabled);
   alert(navigator.platform);
   alert(navigator.userAgent);
**/  
  WriteLogMsg('*Browser_Information ' + navigator.userAgent);
  bname = navigator.appName;
  if(IsMicrosoft()) {
    //var arVersion = navigator.appVersion.split("MSIE");
    //bversion = parseFloat(arVersion[1]);
	 var ua = navigator.userAgent;
    var msie = ua.indexOf('MSIE ');
    if (msie > 0) {
        // IE 10 or older => return version number
        bversion = parseFloat(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
    }

    var trident = ua.indexOf('Trident/');
    if (trident > 0) {
        // IE 11 => return version number
        var rv = ua.indexOf('rv:');
        bversion = parseFloat(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
    }

    var edge = ua.indexOf('Edge/');
    if (edge > 0) {
       // IE 12 => return version number
       bversion = parseFloat(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
    }

  }
  else if(IsNetscape() || IsSafari()) {
    bversion = parseInt(navigator.appVersion);
    //check for Safari.  
    if(navigator.userAgent.match('Safari')) bname = 'Safari';
  }
  else bversion = 0;
}

function IsMicrosoft() {
    var ms_ie = false;
    var ua = navigator.userAgent;
    var old_ie = ua.indexOf('MSIE ');
    var new_ie = ua.indexOf('Trident/');

    if ((old_ie > -1) || (new_ie > -1)) {
    		return true;
		}
	return false;
}


function IsNetscape() {
  var is_firefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
 	return is_firefox;
}
/**
function IsMicrosoft() {
  return (bname.indexOf("Windows")!=-1);
}
**/
function IsSafari() {
   var is_safari = !!navigator.userAgent.match(/Version\/[\d\.]+.*Safari/)
	return is_safari;
}

function IsChrome() {
  var is_chrome = /chrome/i.test( navigator.userAgent );
  return is_chrome;
}

function getCookie(c_name) {
  if (document.cookie.length>0) { 
    c_start=document.cookie.indexOf(c_name + "=");
    if (c_start!=-1) { 
      c_start=c_start + c_name.length+1;
      c_end=document.cookie.indexOf(";",c_start);
      if (c_end==-1) c_end=document.cookie.length;
      return unescape(document.cookie.substring(c_start,c_end));
    } 
  }
  return null
}

function setCookie(c_name,value,expiredays) {
  var exdate=new Date();
  exdate.setDate(expiredays);
  document.cookie=c_name+ "=" +escape(value)+
    ((expiredays==null) ? "" : "; expires="+exdate);
}

// This function gets a variable from the URL (or the COOKIES)
// example: var username = getQueryVariable("username");
function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if (pair[0] == variable) {
            return pair[1];
        }
    }
    return getCookie(variable);
}
