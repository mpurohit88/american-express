import {
  Button
} from '@material-ui/core';

import './button.css';

export const DisableButton = ({ text }) => (
  <Button variant="contained" className="downloadBtn" disabled>
    {text}
  </Button>
)