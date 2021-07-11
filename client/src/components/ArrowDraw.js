import { Arrow } from "react-konva";

const ArrowDraw = ({ startX, startY, x, y }) => {

  return <Arrow points={[startX, startY, x, y]} fill="black" stroke="black" />;
}

export default ArrowDraw;