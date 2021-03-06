// This file contains the scripts for when the draw event is activated.

var draw_anno = null;
var query_anno = null;

// This function is called with the draw event is started.  It can be 
// triggered when the user (1) clicks on the base canvas.
function StartDrawEvent(event) {
  if(!action_CreatePolygon) return;
  if(active_canvas != REST_CANVAS) return;
  
  // Write message to the console:
  console.log('LabelMe: Starting draw event...');

  // If we are hiding all polygons, then clear the main canvas:
  if(IsHidingAllPolygons) {
    for(var i = 0; i < main_canvas.annotations.length; i++) {
      main_canvas.annotations[i].hidden = true;
      main_canvas.annotations[i].DeletePolygon();
    }
  }

  // Set active canvas:
  active_canvas = DRAW_CANVAS;
  if (video_mode) oVP.Pause();
  // Get (x,y) mouse click location and button.
  var x = GetEventPosX(event);
  var y = GetEventPosY(event);
  var button = event.button;
  
  // If the user does not left click, then ignore mouse-down action.
  if(button>1) return;
  
  // Move draw canvas to front:
  $('#draw_canvas').css('z-index','0');
  $('#draw_canvas_div').css('z-index','0');
  
  if(username_flag) submit_username();
  
  // Create new annotation structure:
  var numItems = $(LM_xml).children('annotation').children('object').length;
  draw_anno = new annotation(numItems);
  
  // Add first control point:
  draw_anno.pts_x.push(Math.round(x/main_media.GetImRatio()));
  draw_anno.pts_y.push(Math.round(y/main_media.GetImRatio()));
  
  // Draw polyline:
  draw_anno.SetDivAttach('draw_canvas');
  draw_anno.DrawPolyLine();

  // Set mousedown action to handle when user clicks on the drawing canvas:
  $('#draw_canvas_div').unbind();
  $('#draw_canvas_div').mousedown({obj: this},function(e) {
      return DrawCanvasMouseDown(e.originalEvent);
    });

  WriteLogMsg('*start_polygon');
}

// Handles when the user presses the mouse button down on the drawing
// canvas.
function DrawCanvasMouseDown(event) {
  // User right-clicked mouse, so close polygon and return:
  if(event.button > 1) return DrawCanvasClosePolygon();

  // Else, the user left-clicked the mouse.
  if(active_canvas!=DRAW_CANVAS) return;
  if(username_flag) submit_username();

  // Get (x,y) mouse location:
  var scale = main_media.GetImRatio();
  var x = Math.round(GetEventPosX(event)/scale);
  var y = Math.round(GetEventPosY(event)/scale);

  // Add point to polygon:
  draw_anno.pts_x.push(x);
  draw_anno.pts_y.push(y);

  // Create array of line IDs if it is null:
  if(!draw_anno.line_ids) draw_anno.line_ids = Array();
  
  var line_idx = draw_anno.line_ids.length;
  var n = draw_anno.pts_x.length-1;
  
  // Draw line segment:
  draw_anno.line_ids.push(DrawLineSegment(draw_anno.div_attach,draw_anno.pts_x[n-1],draw_anno.pts_y[n-1],draw_anno.pts_x[n],draw_anno.pts_y[n],'stroke="#0000ff" stroke-width="4"',scale));

  // Set cursor to be crosshair on line segment:
  $('#'+draw_anno.line_ids[line_idx]).css('cursor','crosshair');
  
  // Move the first control point to be on top of any drawn lines.
  $('#'+draw_anno.div_attach).append($('#'+draw_anno.point_id));
}    

// Handles when the user closes the polygon by right-clicking or clicking 
// on the first control point.
function DrawCanvasClosePolygon() {
  if(active_canvas!=DRAW_CANVAS) return;
  if(username_flag) submit_username();
  if((object_choices!='...') && (object_choices.length==1)) {
    main_handler.SubmitQuery();
    StopDrawEvent();
    return;
  }
  active_canvas = QUERY_CANVAS;
  
  // Move draw canvas to the back:
  document.getElementById('draw_canvas').style.zIndex = -2;
  document.getElementById('draw_canvas_div').style.zIndex = -2;
  
  // Remove polygon from the draw canvas:
  var anno = null;

  if(draw_anno) {
    draw_anno.DeletePolygon();
    anno = draw_anno;
    draw_anno = null;
  }
  
  // Move query canvas to front:
  document.getElementById('query_canvas').style.zIndex = 0;
  document.getElementById('query_canvas_div').style.zIndex = 0;
  
  // Set object list choices for points and lines:
  var doReset = SetObjectChoicesPointLine(anno.GetPtsX().length);

  // Get location where popup bubble will appear:
  var pt = main_media.SlideWindow(Math.round(anno.GetPtsX()[0]*main_media.GetImRatio()),Math.round(anno.GetPtsY()[0]*main_media.GetImRatio()));

  // Make query popup appear.
  main_media.ScrollbarsOff();
  WriteLogMsg('*What_is_this_object_query');
  if (video_mode){
    var html_str = "<b>Enter object name</b><br />";
    html_str += HTMLobjectBox("");
    
    if(use_attributes) {
      html_str += HTMLoccludedBox("");
      html_str += "<b>Enter attributes</b><br />";
      html_str += HTMLattributesBox("");
    }
    if(use_parts) {
      html_str += HTMLpartsBox("");
    }
    html_str += "<br />";
  
    // Done button:
    html_str += '<input type="button" value="Done" title="Press this button after you have provided all the information you want about the object." onclick="main_media.SubmitObject();" tabindex="0" />';
  
    // Undo close button:
    html_str += '<input type="button" value="Undo close" title="Press this button if you accidentally closed the polygon. You can continue adding control points." onclick="UndoCloseButton();" tabindex="0" />';
  
    // Delete button:
    html_str += '<input type="button" value="Delete" title="Press this button if you wish to delete the polygon." onclick="scribble_canvas.WhatIsThisObjectDeleteButton();" tabindex="0" />';
    



    CreatePopupBubble(pt[0],pt[1], html_str, 'main_section');
  } 
  else mkPopup(pt[0],pt[1]);
  
  // If annotation is point or line, then 
  if(doReset) object_choices = '...';
  
  // Render annotation:
  query_anno = anno;
  query_anno.SetDivAttach('query_canvas');
  FillPolygon(query_anno.DrawPolygon(main_media.GetImRatio()));
}

// Handles when the user presses the undo close button in response to
// the "What is this object?" popup bubble.
function UndoCloseButton() {
  active_canvas = DRAW_CANVAS;
  
  // Move query canvas to the back:
  document.getElementById('query_canvas').style.zIndex = -2;
  document.getElementById('query_canvas_div').style.zIndex = -2;
  
  // Remove polygon from the query canvas:
  query_anno.DeletePolygon();
  var anno = query_anno;
  query_anno = null;
  
  CloseQueryPopup();
  main_media.ScrollbarsOn();
  
  // Move draw_canvas to front:
  document.getElementById('draw_canvas').style.zIndex = 0;
  document.getElementById('draw_canvas_div').style.zIndex = 0;

  // Draw polyline:
  draw_anno = anno;
  draw_anno.SetDivAttach('draw_canvas');
  draw_anno.DrawPolyLine();
}

// This function is called when the draw event is finished.  It can be
// triggered when the user (1) closes the polygon and only one option is
// valid in the drop-down list (2) erases the last control point.
function StopDrawEvent() {
  // Set active canvas:
  active_canvas = REST_CANVAS;
  if (video_mode) oVP.Play();
  // Move draw canvas to the back:
  $('#draw_canvas').css('z-index','-2');
  $('#draw_canvas_div').css('z-index','-2');

  // Remove polygon from draw canvas:
  if(draw_anno) {
    draw_anno.DeletePolygon();
    draw_anno = null;
  }

  // Write message to the console:
  console.log('LabelMe: Stopped draw event.');
}
