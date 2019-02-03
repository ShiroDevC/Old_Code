#region

using System;
using System.Runtime.Serialization;
using System.Xml.Serialization;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.AI;
using pirates.AI.Pathfinding;
using pirates.GUI;
using pirates.Managers;
using pirates.Map;

#endregion

namespace pirates.GameObjects
{
    /// <summary>
    ///     This class implements the basic attributes of every swimming object.
    ///     All moving units will inherit from this abstract class.
    /// </summary>
    [DataContract(IsReference = true)]
    public abstract class AShip : IGameObject
    {
        #region Properties
        /// <summary>
        ///     The specific Maximum HP for the Ship.
        /// </summary>
        // ReSharper disable once MemberCanBeProtected.Global (needed for Xml Serialization)
        [DataMember]
        public float MaxHp { get; set; } = 100;

        [DataMember]
        public float InitialMovingSpeed { get; set; }

        [XmlIgnore]
        [IgnoreDataMember]
        public Texture2D mShipTexture;

        /// <summary>
        ///     Boolean, stores information about whether the ship is selected or not.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public bool Selected { get; set; }

        /// <summary>
        ///     Boolean to check if the ship is owned by the player or not.
        /// </summary>
        [DataMember]
        public bool Owned { get; set; }

        /// <summary>
        ///     Boolean to set the ship's status to Moving or idling.
        /// </summary>
        [DataMember]
        public bool Moving { get; set; }

        /// <summary>
        ///     Boolean to set the ship's status to Repairing. While Repairing is true, the ship can't move.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public bool Repairing { get; set; }

        /// <summary>
        ///     Boolean to indicate, if an AShip is beeing entered at the moment.
        /// </summary>
        [DataMember]
        public bool IsEntered { get; set; }

        /// <summary>
        ///     A Vector that represents the position of the ship in the World.
        /// </summary>
        // ReSharper disable once MemberCanBePrivate.Global (needed for Xml Serialization)
        [DataMember]
        public Vector2 Position { get; set; }

        /// <summary>
        ///     The Vector of the direction of the ship.
        /// </summary>
        // ReSharper disable once MemberCanBeProtected.Global (needed for Xml Serialization)
        [DataMember]
        public Vector2 Direction { get; set; }

        /// <summary>
        ///     ArrayList with targets, the complete path of the Ship to its destination.
        /// </summary>
        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerialization)
        [DataMember]
        internal Path ShipPath { get; set; }

        /// <summary>
        ///     Integer with the hitpoints of a AShip
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        // ReSharper disable once MemberCanBeProtected.Global
        [DataMember]
        public float Hp { get; set; }

        /// <summary>
        ///     The movementspeed of the ship as a float value, wich will be multiplicated by the
        ///     direction vector. It is the max speed of the boat and also determines the acceleration.
        /// </summary>
        [DataMember]
        public float MovementSpeed { get; set; }

        /// <summary>
        ///     The Movementspeed Upgrade(permanent increase)
        /// </summary>
        [DataMember]
        public float MovementSpeedUpgrade { get; set; }

        /// <summary>
        ///     The current speed, starts at a certain number and grows procentual to te MovementSpeed.
        /// </summary>
        [DataMember]
        protected float ActualMovingSpeed { get; set; }

        /// <summary>
        ///     The free pirates to be sent to the stations.
        /// </summary>
        [DataMember]
        public float FreePirates { get; set; }

        /// <summary>
        ///     The maximun of pirates in the ship.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        // ReSharper disable once MemberCanBeProtected.Global
        [DataMember]
        public int MaxFreePirates { get; set; }

        /// <summary>
        ///     The Attackvalue for the Canons, is equal to the count of pirates at the canon stations.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public int AttackValue { get; set; }

        /// <summary>
        ///     Permanent increase of AttackValue
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public int AttackValueUpgrade { get; set; }

        /// <summary>
        ///     The number of pirates at the deck, ready to fight when entering a ship.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public float EnterAttackValue { get; set; }

        /// <summary>
        ///     Permanent increase of EnterAttackValue
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public float EnterAttackValueUpgrade { get; set; }

        /// <summary>
        ///     The number of pirates at the repair station.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public int RepairingValue { get; set; }

        /// <summary>
        ///     Permanent increase of RepairValue
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public int RepairValueUpgrade { get; set; }

        /// <summary>
        ///     The number of pirates to add to Attack.
        /// </summary>
        [DataMember]
        public int AttackValueToAdd { get; set; }

        /// <summary>
        ///     The number of pirates to add to EnterAttack.
        /// </summary>
        [DataMember]
        public float EnterAttackValueToAdd { get; set; }

        /// <summary>
        ///     The number of pirates to add to Sails(MovementSpeed).
        /// </summary>
        [DataMember]
        public float MovementSpeedToAdd { get; set; }

        /// <summary>
        ///     The number of pirates to add to Repair.
        /// </summary>
        [DataMember]
        public int RepairingValueToAdd { get; set; }

        /// <summary>
        ///     The number of pirates on the ship.
        /// </summary>
        [DataMember]
        public float AllPiratesOnShip { get; set; }

        /// <summary>
        ///     The Bar to draw when entering
        /// </summary>
        public Bar CrewBar { get; set; }

        /// <summary>
        ///     The Bar for the Hp.
        /// </summary>
        public Bar HealthBar { get; set; }

        /// <summary>
        ///     The amount of Rum from the current Buff.
        /// </summary>
        public int RumDrunken { get; set; }

        /// <summary>
        ///     The duration of the RumBuff in seconds.
        /// </summary>
        public double RumBuffDuration { get; set; }

        /// <summary>
        ///     The duration of the RumDeBuff after the Buff in seconds.
        /// </summary>
        private double RumDeBuffDuration { get; set; }

        /// <summary>
        ///     Counts how many times rum was used to buff against the rumDeBuff
        /// </summary>
        private int mCounterRum = 1;

        protected double mPiratesChangeDelay;

        private IGridCell mCurrentCell;

        protected float mShipAngle;

        public bool mWindBoosted;

        public bool mWindSlowed;

        /// <summary>
        ///     Threshold when the Ship will consider going to the next waypoint (Pixles).
        /// </summary>
        private readonly double mNextWaypointThreshold = 20;

        /// <summary>
        ///     Offset for the mNextWaypointThreshold to temporarily increase or decrerase the value of mNextWaypointThreshold.
        ///     (Pixles).
        /// </summary>
        private double mNextWaypointThresholdOffset;

        private const float WindSpeedBoost = 0.2f;

        #endregion

        protected AShip(Vector2 position) : this()
        {
            Position = position;
            Game1.mMapScreen.mGridMap.OccupyCell(Position);
        }

        // ReSharper disable once PublicConstructorInAbstractClass (needed for XmlSerialization)
        public AShip()
        {
            // ReSharper disable once VirtualMemberCallInConstructor
            LoadContent(Game1.mContentManager);
        }

        /// <summary>
        ///     Destructor.
        /// </summary>
        ~AShip()
        {
            if (Game1.mMapScreen != null && Game1.mMapScreen.mGridMap != null && !float.IsNaN(Position.X))
            {
                Game1.mMapScreen.mGridMap.OccupyCell(Position, true);
            }
        }


        /// <summary>
        ///     Sets the ship's status to moving and sets the Path ArrayList for the given target Vector.
        ///     <param name="target"> The target of the movement of the ship</param>
        /// </summary>
        public void Move(Path target)
        {
            if (!Moving)
            {
                ActualMovingSpeed = 0.1f; //resets the speed
            }

            if (target != null)
            {
                ShipPath = target;
                Moving = true;
            }
        }

        /// <summary>
        ///     Update for all Swimming Objects. IsVisible only Movement and the correspondingly input.
        /// </summary>
        public virtual void UpdateMoving(GameTime gameTime)
        {
            //check if there's a rum buff
            if (RumBuffDuration > 0)
            {
                //count the duration of the buff
                RumBuffDuration -= gameTime.ElapsedGameTime.TotalSeconds;
                if (RumBuffDuration <= 0 && RumDrunken > 0)
                {
                    RumBuffDuration = 0;
                    //decrease the Stats
                    MovementSpeed -= 0.2f;
                    AttackValue -= 10;
                    EnterAttackValue -= 10;
                    RepairingValue -= 10;
                    if (RumDeBuffDuration > 0)
                    {
                        mCounterRum++;
                    }
                    RumDeBuffDuration = RumDrunken * 7;
                    RumDrunken = 0;
                }
            }
            else if (RumDeBuffDuration > 0)
            {
                // start counting the debuff when the buff is over
                RumDeBuffDuration -= gameTime.ElapsedGameTime.TotalSeconds;
                if (RumDeBuffDuration <= 0 && RumDrunken == 0 && mCounterRum == 1)
                {
                    RumDeBuffDuration = 0;
                    //decrease the Stats
                    MovementSpeed += 0.1f;
                    AttackValue += 5;
                    EnterAttackValue += 5;
                    RepairingValue += 5;
                }
                else if (RumDeBuffDuration <= 0 && RumDrunken == 0 && mCounterRum > 1)
                {
                    RumDeBuffDuration = 0;
                    //decrease the Stats
                    MovementSpeed += 0.1f * mCounterRum;
                    AttackValue += 5 * mCounterRum;
                    EnterAttackValue += 5 * mCounterRum;
                    RepairingValue += 5 * mCounterRum;
                    mCounterRum = 1;
                }
            }

            //check if pirates need to be relocated
            if (mPiratesChangeDelay <= 0)
            {
                if (AttackValueToAdd > 0)
                {
                    AttackValue++;
                    AttackValueToAdd--;
                }
                if (EnterAttackValueToAdd > 0)
                {
                    EnterAttackValue++;
                    EnterAttackValueToAdd--;
                }
                if (MovementSpeedToAdd > 0)
                {
                    MovementSpeed += 0.01f;
                    MovementSpeedToAdd -= 0.01f;
                }
                if (RepairingValueToAdd > 0)
                {
                    RepairingValue++;
                    RepairingValueToAdd--;
                }
                mPiratesChangeDelay = 0.5;
            }
            else
            {
                mPiratesChangeDelay -= gameTime.ElapsedGameTime.TotalSeconds;
            }

            if (Moving)
            {
                if (!ShipPath.Finished && !IsEntered)
                {
                    // if the ship is sailing with the wind, it gets a speedboost
                    if (mShipAngle >= EnvironmentManager.GetWindDirectionDegrees() - 5 &&
                        mShipAngle <= EnvironmentManager.GetWindDirectionDegrees() + 5 && !mWindBoosted)
                    {
                        MovementSpeed += WindSpeedBoost;
                        mWindBoosted = true;
                    }

                    // when it leaves the windstream the boost vanishes.
                    if (mShipAngle < EnvironmentManager.GetWindDirectionDegrees() - 5 && mWindBoosted ||
                        mShipAngle > EnvironmentManager.GetWindDirectionDegrees() + 5 && mWindBoosted)
                    {
                        MovementSpeed -= WindSpeedBoost;
                        mWindBoosted = false;
                    }

                    if (mShipAngle >= EnvironmentManager.GetInverseWindDirectionDegrees() - 5 &&
                        mShipAngle <= EnvironmentManager.GetWindDirectionDegrees() + 5 && !mWindSlowed)
                    {
                        MovementSpeed -= WindSpeedBoost;
                        mWindSlowed = true;
                    }

                    // when it leaves the windstream the boost vanishes.
                    if (mShipAngle < EnvironmentManager.GetInverseWindDirectionDegrees() - 5 && mWindSlowed ||
                        mShipAngle > EnvironmentManager.GetInverseWindDirectionDegrees() + 5 && mWindSlowed)
                    {
                        MovementSpeed += WindSpeedBoost;
                        mWindSlowed = false;
                    }

                    // Increases the MovementSpeed
                    if (ActualMovingSpeed < MovementSpeed + MovementSpeedUpgrade)
                    {
                        ActualMovingSpeed += (MovementSpeed - ActualMovingSpeed) / 100;
                    }
                    FollowPath(gameTime);
                }
                else
                {
                    Moving = false;
                }
            }
        }

        /// <summary>
        ///     Follow the Path
        /// </summary>
        /// <param name="gameTime"></param>
        private void FollowPath(GameTime gameTime)
        {
            // Make shure we have a valid position.
            if (float.IsNaN(Position.X))
            {
                return;
            }
            // Move to the next Waypoint
            var distanceToNextPoint = Vector2.Distance(Position, ShipPath.Next.Cell.Center);
            if (distanceToNextPoint > mNextWaypointThreshold + mNextWaypointThresholdOffset)
            {
                if (Game1.mAdvancedMovements)
                {
                    if (ShipPath.Next.Predecessor != null)
                    {
                        var nextDirection = ShipPath.Next.Cell.Center - Position;
                        nextDirection.Normalize();

                        var nextNextDirection =
                            ShipPath.Next.Predecessor.Cell.Center - ShipPath.Next.Cell.Center;
                        nextNextDirection.Normalize();

                        var ammount = Math.Max(0, 0.8f - distanceToNextPoint / 16);
                        Direction = Vector2.Lerp(nextDirection, nextNextDirection, ammount);
                        mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                    }
                    else
                    {
                        Direction = ShipPath.Next.Cell.Center - Position;
                        mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                    }
                }
                else
                {
                    Direction = ShipPath.Next.Cell.Center - Position;
                    mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                }

                // Collision avoidance
                Direction = CollisionAvoidance(Direction, gameTime);
                mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                var addToPosition = Direction * 150 * (float) gameTime.ElapsedGameTime.TotalSeconds * ActualMovingSpeed;
                Position += addToPosition;
            }
            else
            {
                ShipPath.GetNextWaypoint();
                mNextWaypointThresholdOffset = 0;
            }

            // Update the occupied cells.
            var cellAtPosition =
                Game1.mMapScreen.mGridMap.GetCell(Game1.mMapScreen.mGridMap.PosToGrid(Position).ToPoint());
            if (mCurrentCell != cellAtPosition)
            {
                if (mCurrentCell != null)
                {
                    mCurrentCell.Occupied = false;
                }
                Game1.mMapScreen.mGridMap.OccupyCell(Position, Direction);
                mCurrentCell = cellAtPosition;
            }
        }

        /// <summary>
        ///     Calculate the new Direction in case we have to avoide some opponents.
        /// </summary>
        /// <param name="direction"></param>
        /// <param name="gameTime"></param>
        /// <returns></returns>
        private Vector2 CollisionAvoidance(Vector2 direction, GameTime gameTime)
        {
            direction = Vector2.Normalize(direction); // Normalize direction for a constant speed.

            var gridMap = Game1.mMapScreen.mGridMap;
            var cellsAhead = gridMap.GetCellsInDirection(gridMap.GetCell(Position), direction, 4, 2);
            var numberOfOpponents = 0;
            var sumOfForce = 0d;
            var avoidanceVector = Vector2.Zero;

            foreach (var cell in cellsAhead)
            {
                if (cell.Occupied)
                {
                    numberOfOpponents++;
                    // Distance to the opponent.
                    var distance = Vector2.Distance(Position, cell.Center);
                    // Force of the opponent pushing us away.
                    var force = Helpers.Force(distance);
                    sumOfForce += force;
                    // var vectorToOccupent = Vector2.Normalize(Position - cell.Center);
                    avoidanceVector += (float) force * (Position - cell.Center);
                }
            }
            if (numberOfOpponents != 0 && sumOfForce > 0.1)
            {
                // Normalize everithing.
                avoidanceVector = Vector2.Normalize(avoidanceVector);
                direction += (float) (sumOfForce / numberOfOpponents) * avoidanceVector;
                // Add an estimated distance to the next waypoint offset 
                // to enable skipping waypoints in case of bigger distance traveled because avoidance pushes us off route.
                mNextWaypointThresholdOffset += 150 * sumOfForce * (float) gameTime.ElapsedGameTime.TotalSeconds *
                                                ActualMovingSpeed;
                direction.Normalize();
            }
            return direction;
        }

        /// <summary>
        ///     Drops resources of a specific range. Depends from the type of Ship that is destroyed.
        ///     Adds the random numbers directly to the Resources of the player.
        /// </summary>
        public abstract void DropLoot();

        public abstract void Initialize();

        /// <summary>
        ///     Load Assets.
        ///     Since this is called by the constructor don't ever call this from somewhere else.
        /// </summary>
        /// <param name="content"></param>
        public abstract void LoadContent(ContentManager content);
    }
}