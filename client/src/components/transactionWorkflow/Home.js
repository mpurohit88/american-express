import React, { useState } from 'react';

import {
  Box,
  Container,
  Grid
} from '@material-ui/core';

import BusinessEntity from './BusinessEntity';
import Workflow from './Workflow';

const Home = () => {
  const [rectDraw, setRectDraw] = useState([])

  const removeEntity = (entityName) => {
    setRectDraw(rectDraw.filter(entity => entity !== entityName));
  }

  const drawRect = (entity) => {
    setRectDraw([...rectDraw, entity])
  }

  return <Box
    sx={{
      backgroundColor: 'background.default',
      minHeight: '100%',
      py: 10
    }}
  >
    <Container maxWidth={false}>
      <Grid
        container
        spacing={3}
      >
        <Grid
          item
          lg={3}
          md={6}
          xl={3}
          xs={12}
        >
          <BusinessEntity rectDraw={rectDraw} drawRect={drawRect} />
        </Grid>
        <Grid
          item
          lg={9}
          md={12}
          xl={9}
          xs={12}
        >
          <Workflow rectDraw={rectDraw} removeEntity={removeEntity} />
        </Grid>
      </Grid>
    </Container>
  </Box>;
}

export default Home;