using System;
using System.Collections.Generic;
using System.Runtime.Serialization;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using MonoGame.Extended.Shapes;
using pirates.Managers;

namespace pirates.GameObjects
{
    public sealed class Dragon: AShip
    {
        /// <summary>
        ///  Enum for the different Battlestates the Ship can be in.
        /// </summary>
        public enum ShipBattleState { Attacking, Idle }

        /// <summary>
        ///  Instance of the BattleState enum. To be used at the Updateloop.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public ShipBattleState CurrentBState { get; private set; }

        [DataMember]
        public AShip TargetShip { get; set; }
        /// <summary>
        ///  The targetvector of the Dragon(flies)
        /// </summary>
        private Vector2 MovementTarget { get; set; }

        [DataMember]
        public bool Chasing { get; set; }

        [DataMember]
        private double mShootingDelay;

        public Dragon(Vector2 position) : base(position)
        {
            Initialize();
        }

        // ReSharper disable once UnusedMember.Global (needed for Xml Serialization.)
        public Dragon()
        {

        }

        public override void DropLoot()
        {
            var random = new Random();
            var number = random.Next(100, 300);
            RessourceManager.AddRessource("wood", number);
            number = random.Next(20, 30);
            RessourceManager.AddRessource("gold", number);
            RessourceManager.AddRessource("mapParts", 1);
        
        }

        public override void Initialize()
        {
            CurrentBState = ShipBattleState.Idle;
            MaxHp = 200;
            Hp = (int)MaxHp;
            MaxFreePirates = 80;
            AttackValue = 30;
            EnterAttackValue = 0f;
            RepairingValue = 0;
            MovementSpeed = 0.15f;
            InitialMovingSpeed = 0.15f;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/dragonsprite");
        }

        public void Attack(AShip target)
        {
            CurrentBState = ShipBattleState.Attacking;
            TargetShip = target;

        }
        /// <summary>
        /// Movement Method with vectors only for the Dragon
        /// </summary>
        public void MoveDragon(Vector2 target)
        {
            if (!Moving)
            {
                ActualMovingSpeed = 0.1f;//resets the speed
                Moving = true;
            }
            MovementTarget = target;
            
        }


        public void UpdateDragonMovement(GameTime gameTime)
        {
            if (!Moving) return;
            var distanceToNextPoint = Vector2.Distance(Position, MovementTarget);
            if (distanceToNextPoint > 20)
            {
                if (Game1.mAdvancedMovements)
                {
                    
                    Direction = (MovementTarget - Position);
                    mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                    
                }
                else
                {
                    Direction = (MovementTarget - Position);
                    mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                }

                Direction = Vector2.Normalize(Direction); // Normalize direction for a constant speed.
                mShipAngle = MathHelper.ToDegrees((float) Math.Atan2(Direction.Y, Direction.X)) + 180;
                Position += (Direction * 150 * (float) gameTime.ElapsedGameTime.TotalSeconds) * ActualMovingSpeed;
            }
            else
            {
                Moving = false;
            }
        }

        public void Update(GameTime gameTime, QuadTree quadTree)
        {
            if (Hp <= 0)
            {
                CurrentBState = ShipBattleState.Idle;
            }
            if (CurrentBState == ShipBattleState.Attacking && TargetShip != null
                && ((!TargetShip.Owned && Owned) || (!Owned && TargetShip.Owned)))
            {
                Chasing = TargetShip.Moving;

                if (Vector2.Distance(Position, TargetShip.Position) <= 150f)
                {
                    if (!Chasing)
                    {
                        Moving = false;
                    }
                    else if (Vector2.Distance(Position, TargetShip.Position) <= 100f)
                    {
                        Moving = false;
                    }


                    //Chasing = false;
                    //if a movement command is set, the ship will only move and stop shooting

                    //shooting
                    mShootingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    if (mShootingDelay <= 0 && TargetShip.Hp > 0)
                    {
                        Game1.mMapScreen.ShootBullet(Position, TargetShip.Position);
                        mShootingDelay = 3f;//reset the timer
                        TargetShip.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);
                        //now deal damage to the Ships around the TargetShip
                        var possibleCollisions = new List<AShip>();
                        quadTree.Retrieve(possibleCollisions, TargetShip);
                        foreach (var potentialVictim in possibleCollisions)
                        {
                            //only dmg ships in a certain range
                            var rangeCircle = new CircleF(TargetShip.Position, 40f); //scan radius
                            if (rangeCircle.Contains(potentialVictim.Position) && potentialVictim.Owned &&
                                 potentialVictim.Hp >= 0)
                            {
                                potentialVictim.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);//dmg dealed
                            }
                        }
                        
                        if (TargetShip.Hp <= 0)
                        {
                            Game1.mMapScreen.Drowning(TargetShip.Position, 6);
                            CurrentBState = ShipBattleState.Idle;
                            TargetShip = null;
                        }

                    }
                    else if (TargetShip.Hp <= 0)
                    {
                        CurrentBState = ShipBattleState.Idle;
                        TargetShip = null;
                    }
                }
            }
        }
    }
}
