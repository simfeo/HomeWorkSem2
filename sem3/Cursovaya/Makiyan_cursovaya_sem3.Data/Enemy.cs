﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Drawing;
using System.Runtime.Serialization;

namespace MarketInfo.Data
{
    [DataContract(Name ="Enemy")]
    public class Enemy : BaseMovingGameElement
    {
        public Enemy(Point initPoint) : base("enemy", initPoint)
        {

        }
    }
}
