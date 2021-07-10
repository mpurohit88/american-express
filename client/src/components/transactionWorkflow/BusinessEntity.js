import React from 'react';
import { useSelector } from 'react-redux';
import {
  Box,
  Typography
} from '@material-ui/core';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';

import { Heading } from '../materialUI';

import './BusinessEntity.css';

export default function BusinessEntity({ rectDraw, drawRect }) {
  const businessEntity = useSelector(state => state.businessEntity);

  return <>
    <Heading text="Business Entity" />
    <Box
      sx={{
        pt: 2,
        display: 'flex',
        alignItems: 'center'
      }}
    >
      {
        (rectDraw.length === businessEntity.length) ? null : <><ArrowDownwardIcon sx={{ color: "red" }} />
          <Typography
            color="textSecondary"
            variant="caption"
          >
            Click on entity to add in workflow
          </Typography> </>
      }
    </Box>
    <ul>
      {
        (businessEntity || []).map((entity, index) => {
          if (rectDraw.find(element => element === entity)) return null;

          return <li key={index} onClick={() => drawRect(entity)}>{entity}</li>
        })
      }
    </ul>

  </>
}