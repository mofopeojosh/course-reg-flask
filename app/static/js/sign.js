var signature = (function () {
  var canvas = document.getElementByID('signature');
  var parent = document.getElementByID('wrapper');
  var context = canvas.getContext('2D');
  empty = true;

  return{ 
      capture: function (){
        if (!context){
          throw new Error("Failed to get canvas, 2d context")
        }
        // screenwidth = screen.width;

        context.fillStyle = "#fff";
        context.strokeStyle = "#444";
        context.lineWidth = 1,2;
        context.lineCap = "round";

        context.fillRect(0, 0, canvas.width, canvas.height);

        context.fillStyle = "#3a87ad";
				context.strokeStyle = "#3a87ad";
				context.lineWidth = 1;
				context.moveTo((canvas.width * 0.042), (canvas.height * 0.7));
				context.lineTo((canvas.width * 0.958), (canvas.height * 0.7));
				context.stroke(); 

        context.fillStyle = "#fff";
				context.strokeStyle = "#444";
        
        var disableSave = true;
				var pixels = [];
				var cpixels = [];
				var xyLast = {};
				var xyAddLast = {};
				var calculate = false;

				//functions
        {
          function get_coords(e){
            var x, y;

            if (e.changedTouches && e.changedTouches[0]){
              var offsety = canvas.offsetTop || 0;
              var offsetx = canvas.offsetLeft || 0;
              
              x = e.changedTouches[0].pageX - offsetx;
              y = e.changedTouches[0].pageY - offsety;
            }
            else if (e.layerX||0 == e.layerX){
               x = e.layerX;
               y = e.layerY;
            }  
            else if (e.offsetX||0 == e.offsetX){
               x = e.offsetX;
               y = e.offsetY;
            } 

            return{
              x: x,
              y: y
            };      
          };
          function remove_event_listeners(){
            canvas.removeEventListener('mousemove', on_mousemove, false);
            canvas.removeEventListener('mouseup', on_mouseup, false);
            canvas.removeEventListener('touchmove', on_touchmove, false);
            canvas.removeEventListener('touchend', on_touchend, false);

            document.removeEventListener('mouseup', on_mouseup, false);
            document.removeEventListener('touchend', on_touchend, false);
          };
          function on_mousedown(e){
            e.preventDefault();
            e.stopPropagation();
            
            canvas.addEventListener('mousemove', on_mousemove, false);
            canvas.addEventListener('mouseup', on_mouseup, false);
            canvas.addEventListener('touchmove', on_touchmove, false);
            canvas.addEventListener('touchend', on_touchend, false);

            document.addEventListener('mouseup', on_mouseup, false);
            document.addEventListener('touchend', on_touchend, false);

            empty = false;
            var xy = get_coords(e);
            context.beginPath();
            pixels.push('moveStart');
            context.moveTo(xy.x, xy.y);
            pixels.push(xy.x, xy.y);
            xyLast = xy;

          };
          function on_mousemove(e){
            e.preventDefault();
            e.stopPropagation();
            
            var xy = get_coords(e);
            var xyAdd = {
              x: {xyLast.x + xy}
            };
            context.beginPath();
            pixels.push('moveStart');
            context.moveTo(xy.x, xy.y);
            pixels.push(xy.x, xy.y);
            xyLast = xy;

            if(calculate){
              var xlast =(xyAddLast.x + xyLast +xyAdd.x)/3;
              var ylast =(xyAddLast.y + yyLast +yyAdd.y)/3;
              pixels.push(xLast, yLAst);
            }
            else{ calculate = true; }

            context.quadraticCurveTo(xyLast.x, xyLast.y, xyAdd.x, xyAdd.y);
            pixels.push(xyAdd.x, xyAdd.y);
            context.stroke();
            context.beginPath();
            context.moveTo(xyAdd.x, xyAdd.y)
            xyAddLast = xyAdd;
            xyLast = xy;

          };
          function on_mouseup(){
            remove_event_listners();
            disableSave =false;
            context.stroke();
            pixels.push('e');
            calculate = false;
          };
        }
        
      },
      save: function (){
        var image_data = canvas.toDataURL();
        var image_input = document.getElementById('image_input');
        var form = document.getElementById('save_image');
        image_input.value = image_data;
        form.submit();

      },
      clear: function(){
        parent.removeChild(canvas);
        empty = true;
        // context.clearRect(0, 0, canvas.width, canvas.width);
      }
  }
});