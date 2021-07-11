import React, { useState } from 'react';

import {
  Box,
  Container,
  Grid
} from '@material-ui/core';

import BusinessEntity from './BusinessEntity';
import Workflow from './Workflow';

const Home = () => {
  const [workflow, setWorkflow] = useState([])

  const removeEntity = (entityName) => {
    setWorkflow(workflow.filter(entity => entity !== entityName));
  }

  const addWorkflow = (entity) => {
    setWorkflow([...workflow, entity])
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
          <BusinessEntity workflow={workflow} addWorkflow={addWorkflow} />
        </Grid>
        <Grid
          item
          lg={9}
          md={12}
          xl={9}
          xs={12}
        >
          <Workflow workflow={workflow} removeEntity={removeEntity} />
        </Grid>
      </Grid>
    </Container>
  </Box>;
}

export default Home;