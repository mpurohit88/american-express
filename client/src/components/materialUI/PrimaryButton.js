import {
  Button
} from '@material-ui/core';

import './button.css';

export const PrimaryButton = ({ text, onClick }) => (
  <Button variant="contained" color="primary" className="downloadBtn" onClick={onClick} >
    {text}
  </Button>
)