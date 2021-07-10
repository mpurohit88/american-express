import {
  Typography
} from '@material-ui/core';

const Heading = ({ text }) => (
  <Typography
    color="textSecondary"
    gutterBottom
    variant="h6"
  >
    {text}
  </Typography>
)

export { Heading };