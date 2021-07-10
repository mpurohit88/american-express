import React from 'react';
import {
  Box,
  Typography
} from '@material-ui/core';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import Canvas from '../Canvas';

import {
  Heading,
  PrimaryButton,
  DisableButton
} from '../materialUI';

import './Home.css';

export default function Workflow({ removeEntity, rectDraw }) {
  const downloadSchema = () => {

  }

  return <div className="border">
    <div className="heading">
      <Heading text="Transaction Workflow Model" />
      {
        rectDraw.length === 0 ?
          <DisableButton text="Download" />
          :
          <PrimaryButton onClick={downloadSchema} text="Download" />
      }
    </div>

    <Box
      sx={{
        pt: 2,
        display: 'flex',
        alignItems: 'center'
      }}
    >
      {
        rectDraw.length > 0 ? <><ArrowDownwardIcon sx={{ color: "red" }} />
          <Typography
            color="textSecondary"
            variant="caption"
          >
            Click on entity to remove from workflow
          </Typography> </> : null
      }
    </Box>
    <Canvas rectDraw={rectDraw} removeEntity={removeEntity} />
  </div>
}