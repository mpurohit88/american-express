import React from 'react';
import { Stage, Layer, Rect, Text } from 'react-konva';

// https://codesandbox.io/s/vue-konva-drawings-rectangles-ivjtu?file=/src/App.vue:468-522
const Canvas = ({ rectDraw, removeEntity }) => {
  const rectSize = { width: 150, height: 50 };

  const handleClick = (e) => {
    if (e.target.attrs.text) {
      removeEntity(e.target.attrs.text);
    }
  }

  let xAxisValue = 20;
  const distanceBWBox = 100;

  return (
    <Stage width={window.innerWidth} height={window.innerHeight} onClick={handleClick}>
      <Layer>
        {
          rectDraw.map((rect, index) => {
            xAxisValue = index === 0 ? xAxisValue : xAxisValue + rectSize.width + distanceBWBox;

            return <>
              <Rect
                x={xAxisValue}
                y={20}
                width={rectSize.width}
                height={rectSize.height}
                fill="white"
                shadowBlur={10}
              />
              <Text
                x={xAxisValue + 40}
                y={20}
                width={rectSize.width}
                height={rectSize.height}
                text={rect}
                verticalAlign="middle"
              />
            </>
          })
        }
      </Layer>
    </Stage>
  );
};

export default Canvas;