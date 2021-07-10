import { AppBar, Toolbar } from '@material-ui/core';

const MainNavbar = () => (
  <AppBar
    elevation={0}
  >
    <Toolbar sx={{ height: 64 }}>
      American Express | Transaction Worflow Excercise
    </Toolbar>
  </AppBar>
);

export default MainNavbar;