using System.Collections.Generic;
using System.Runtime.Serialization;
using Microsoft.Xna.Framework;
using pirates.AI.Pathfinding;
using System;
using Microsoft.Xna.Framework.Graphics;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Class for Fleets for the AiShipManager. Manages Fleet-attacks and other actions for a group of ships.
    /// </summary>
    [DataContract]
    public sealed class Fleet
    {
        /// <summary>
        ///  List of all Battleships in the fleet.
        /// </summary>
        [DataMember]
        public List<BattleShip> BattleShips { get; set; }

        /// <summary>
        ///  List of all Tradingships in the fleet.
        /// </summary>
        [DataMember]
        public List<TradingShip> TradingShips { get; set; }


        /// <summary>
        ///  The general Position of the Fleet. This position is used to Scan for enemyships.
        /// </summary>
        private Vector2 Position => FlagShip.Position;

        /// <summary>
        /// The FlagShip of the Fleet. The Fleets position is the FlagShip's position.
        /// </summary>
        [DataMember]
        public AShip FlagShip { get; set; }

        /// <summary>
        ///  List of already detected and attacked enemyships. 
        ///  Newly detected ships will be dynamicaly added here.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        [DataMember]
        public List<AShip> MarkedShips
        {
            get; set;
        }

        [DataMember]
        private List<BattleShip> mEnteringShipsList;

        [DataMember]
        private List<IBattleObject> mAttackingShipsList;

        [DataMember]
        private List<AShip> mRepairingShipsList;

        [DataMember]
        private List<IBattleObject> mDefendingShipsList;

        // ReSharper disable once UnusedMember.Global
        [DataMember]
        public bool Moving { get; set; }
        
        private static PathFinder PathFinder => Game1.mMapScreen.mPathFinder;

        /// <summary>
        /// Indicates if the fleet is attacking other ships or not.
        /// </summary>
        [DataMember]
        public bool InBattle { get; set; }

        /// <summary>
        /// Indicates if the fleet is patrouling or not.
        /// </summary>
        [DataMember]
        public bool Defending { get; set; }

        /// <summary>
        /// Array for mamaging which enemy ship is already about to be entered.
        /// </summary>
        [DataMember]
        private int[] mTobeEntered;

        /// <summary>
        ///  Creates all Ships according to the specified numbers.
        ///  BattleShips and TradingShips need to be added to the allShipsList in the AIShipManager
        /// </summary>
        //bShipCount + tShipCount muss >= 1 sein!!
        public Fleet(Vector2 position,int bShipsCount, int tShipsCount,
            List<BattleShip> enterList, List<IBattleObject> attackingList, List<IBattleObject> defendingList, List<AShip> repairingList)
        {
            BattleShips = new List<BattleShip>();
            TradingShips = new List<TradingShip>();
            MarkedShips = new List<AShip>();

            mEnteringShipsList = enterList;
            mAttackingShipsList = attackingList;
            mRepairingShipsList = repairingList;
            mDefendingShipsList = defendingList;
            //FlagShip
            if (bShipsCount >= 1)
            {
                var bShip = new BattleShip(position)
                {
                    Owned = false,
                    mShipTexture = Game1.mContentManager.Load<Texture2D>("Ships/enemy_ship_texture")
                };
                bShip.Initialize();
                BattleShips.Add(bShip);
                bShipsCount--;
                FlagShip = bShip;
                FlagShip.MovementSpeed = 0.25f;

            }else if (tShipsCount >= 1)
            {
                var tShip = new TradingShip(position);
                tShip.Initialize();
                TradingShips.Add(tShip);
                tShipsCount--;
                FlagShip = tShip;
                FlagShip.MovementSpeed = 0.25f;
            }

            //simple spawn algorithm for testing
            for (var i = 0; i <bShipsCount+tShipsCount; i++)
            {
                //second row
                if (i >= (bShipsCount + tShipsCount)/2)
                {
                    if (i <= bShipsCount)//spawn battleShip
                    {

                        var bShip = new BattleShip(new Vector2((position.X - (((bShipsCount + tShipsCount)/2) * 75) + (i * 50)),position.Y + 100f));// spawn a row of ships on top of the FlagShip
                        BattleShips.Add(bShip);
                    }
                    else if (i <= bShipsCount+tShipsCount)//spawn tradingShip
                    {
                        var tShip = new TradingShip(new Vector2((position.X - (((bShipsCount + tShipsCount) / 2) * 75) + (i * 50)),
                                    position.Y + 100f)) {MovementSpeed = 0.25f};
                        TradingShips.Add(tShip);
                    }
                    
                }
                else//first row
                {
                    if (i <= bShipsCount)//spawn battleShip
                    {
                        var bShip = new BattleShip(new Vector2((position.X - (((bShipsCount + tShipsCount) / 4) * 50) + (i * 50)), position.Y - 100f));// spawn a row of ships on top of the FlagShip
                        bShip.Initialize();
                        BattleShips.Add(bShip);
                    }
                    else if (i <= bShipsCount + tShipsCount)//spawn tradingShip
                    {
                        var tShip = new TradingShip(new Vector2((position.X - (((bShipsCount + tShipsCount) / 4) * 50) + (i * 50)), position.Y - 100f));
                        tShip.Initialize();
                        tShip.MovementSpeed = 0.25f;
                        TradingShips.Add(tShip);
                    }
                }    
            }


        }

        public void UpdateBattle()
        {
            foreach (var bShip in BattleShips)
            {

                if (bShip.CurrentBState == BattleShip.ShipBattleState.Idle)
                {
                    //if there are enemy ships left, attack the next one
                    if (MarkedShips.Count > 0)
                    {
                        bShip.Move(PathFinder.CalculatePath(bShip.Position, MarkedShips[0].Position, true));
                        var random = new Random();
                        var number = random.Next(0, 2);
                        if (number == 0 &&((MarkedShips[0].EnterAttackValue - 8) > bShip.EnterAttackValue))//additional 50% chance to not enter
                        {
                            bShip.Enter(MarkedShips[0]);
                            if (!mEnteringShipsList.Contains(bShip))
                            {
                                mEnteringShipsList.Add(bShip);
                            }
                        }
                        else
                        {
                            bShip.Attack(MarkedShips[0]);
                            if (!mAttackingShipsList.Contains(bShip))
                            {
                                mAttackingShipsList.Add(bShip);
                            }
                        }
                    }
                }
            }
            foreach (var tShip in TradingShips)
            {
                if (tShip.CurrentBState == TradingShip.ShipBattleState.Idle)
                {
                    //if there are enemy ships left, attack the next one
                    if (MarkedShips.Count > 0)
                    {
                        tShip.Move(PathFinder.CalculatePath(tShip.Position, MarkedShips[0].Position, true));
                        tShip.Attack(MarkedShips[0]);
                        if (!mAttackingShipsList.Contains(tShip))
                        {
                            mAttackingShipsList.Add(tShip);
                        }
                    }
                }
            }
        }


        /// <summary>
        ///  Moves the whole fleet in formation to the specified Position.
        /// <param name="destination"> The Vector to move to</param>
        /// </summary>
        public void Move(Vector2 destination)
        {
            //find the closest ship to the destination
            var closestShip = FlagShip;
            var distance = Vector2.Distance(FlagShip.Position, destination);
            foreach (var bShip in BattleShips)
            {
                var newDistance = Vector2.Distance(bShip.Position, destination);
                if (!(distance > newDistance)) continue;
                closestShip = bShip;
                distance = newDistance;
            }
            foreach (var tShip in TradingShips)
            {
                var newDistance = Vector2.Distance(tShip.Position, destination);
                if (!(distance > newDistance)) continue;
                closestShip = tShip;
                distance = newDistance;
            }

            
            //set Movement Commands
            var destinationAddition = new Vector2(0,0);
            foreach (var bShip in BattleShips)
            {
                if (!bShip.Equals(closestShip))
                {
                    destinationAddition = Vector2.Normalize(closestShip.Position - bShip.Position) * 100;
                }

                bShip.Move(PathFinder.CalculatePath(bShip.Position, destination - destinationAddition, false));
                //bShip.Move(PathFinder.CalculatePath(bShip.Position, destination + (bShip.Position - Position), false));
            }
            foreach (var tShip in TradingShips)
            {
                if (!tShip.Equals(closestShip))
                {
                    destinationAddition = Vector2.Normalize(closestShip.Position - tShip.Position) * 100;
                }

                tShip.Move(PathFinder.CalculatePath(tShip.Position, destination - destinationAddition, false));
                //tShip.Move(PathFinder.CalculatePath(tShip.Position, destination + (tShip.Position - Position), false));
            }
        }

        /// <summary>
        ///  Lets the fleet attack all ships in the List. 
        ///  Every Ship in the fleet will get an adjusted order.
        ///  Enter(), Attack() and Defend() are the possible orders.
        /// <param name="toAttack"> The List of Ships to attack</param>
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        // ReSharper disable once UnusedParameter.Global
        // ReSharper disable once UnusedParameter.Global
        // ReSharper disable once UnusedParameter.Global
        public void Attack(List<AShip> toAttack)
        {
            mTobeEntered = new int[toAttack.Count];
            InBattle = true;
            toAttack.Sort(CompareShipsByDistance);
            var counter = 0;
            //now give every Ship in the fleet an attack command
            foreach (var bShip in BattleShips)
            {
                if (toAttack.Count < counter + 1) counter = 0;

                var random = new Random();
                var randomNumber = random.Next(0, 2);//probability to enter for each ship of the fleet
                if ((toAttack[counter].EnterAttackValue - 8) < bShip.EnterAttackValue && mTobeEntered[counter] == 0 && randomNumber == 1)
                {
                    bShip.Enter(toAttack[counter]);
                    mEnteringShipsList.Add(bShip);
                    mTobeEntered[counter] = 1;
                }
                else
                {
                    bShip.Attack(toAttack[counter]);
                    bShip.Move(PathFinder.CalculatePath(bShip.Position, toAttack[counter].Position, true));
                    if (!mAttackingShipsList.Contains(bShip))
                    {
                        mAttackingShipsList.Add(bShip);
                    }
                }
                counter++;
            }

            foreach (var tShip in TradingShips)
            {
                if (toAttack.Count <= counter) counter = 0;

                tShip.Attack(toAttack[counter]);
                counter++;
            }

            MarkedShips.AddRange(toAttack.Count > (BattleShips.Count + TradingShips.Count) ? toAttack.GetRange(0, counter) : toAttack);
        }

        public void StopBattle()
        {
            foreach(var bShip in BattleShips)
                {
                switch (bShip.CurrentBState)
                {
                    case BattleShip.ShipBattleState.Attacking:
                        bShip.CurrentBState = BattleShip.ShipBattleState.Idle;

                        mAttackingShipsList.Remove(bShip);

                        break;
                    case BattleShip.ShipBattleState.Entering:
                        bShip.CurrentBState = BattleShip.ShipBattleState.Idle;
                        mEnteringShipsList.Remove(bShip);
                        break;

                }
            }
            foreach (var tShip in TradingShips)
            {
                switch (tShip.CurrentBState)
                {
                    case TradingShip.ShipBattleState.Attacking:
                        tShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                        mAttackingShipsList.Remove(tShip);
                        break;
                }
            }
        }

        /// <summary>
        /// Compares two ships by their distance to the fleets main position.
        /// </summary>
        private int CompareShipsByDistance(AShip ship1, AShip ship2)
        {
            return Vector2.Distance(Position, ship1.Position) > Vector2.Distance(Position, ship2.Position) ? 1 : 0;
        }
        
        /// <summary>
        /// Returns the number of all ships in the fleet.
        /// </summary>
        public int FleetCount()
        {
            return (BattleShips.Count + TradingShips.Count);
        }
        
    }
}
