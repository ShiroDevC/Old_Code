using System;
using System.Runtime.Serialization;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.AI.Pathfinding;
using pirates.Managers;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Class for all BattleShips. Adds Battle functionality to the AShip.
    /// </summary>
    public class BattleShip : AShip, IBattleObject, IUpdatableObject
    {

        /// <summary>
        ///  Enum for the different Battlestates the Ship can be in.
        /// </summary>
        public enum ShipBattleState { Attacking, Defending, Entering, Idle}

        /// <summary>
        ///  Instance of the BattleState enum. To be used at the Updateloop.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public ShipBattleState CurrentBState { get; set; }

        /// <summary>
        ///  The Target Ship of the battleaction.
        /// </summary>
        [DataMember]
        public AShip TargetShip { get; set; }

        /// <summary>
        ///  Indicates if the Entering Ship is about to dock to the other ship or if its not close enough.
        /// </summary>
        [DataMember]
        public bool Docking { get; private set; }

        [DataMember]
        public bool Chasing { get; set; }
        
        [DataMember]
        private double mShootingDelay;

        public BattleShip(Vector2 position) : base(position)
        {
            // ReSharper disable once VirtualMemberCallInConstructor
            Initialize();
        }

        protected BattleShip()
        {
        }

        /// <summary>
        ///  Gives the Battleship the standard distribution of the pirates.
        /// </summary>
        public override void Initialize()
        {
            CurrentBState = ShipBattleState.Idle;
            MaxHp = 100;
            Hp = (int) MaxHp;
            MaxFreePirates = 40;
            AttackValue = 15;
            EnterAttackValue = 15f;
            RepairingValue = 5;
            MovementSpeed = 0.23f;
            InitialMovingSpeed = 0.23f;
            AllPiratesOnShip = 35;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/battle_ship_texture");
            
        }

        public void Update(GameTime gameTime)
        {
            if (CurrentBState == ShipBattleState.Entering && TargetShip != null)
            {
                if ((!Owned && !TargetShip.Owned) || (Owned && TargetShip.Owned))
                {
                    CurrentBState = ShipBattleState.Idle;
                    TargetShip.IsEntered = false;
                    IsEntered = false;
                    SoundManager.StopAmb("board");
                    Docking = false;
                }
                
            }

            if (CurrentBState != ShipBattleState.Entering && Docking)
            {
                
                Docking = false;
                if (TargetShip != null) TargetShip.IsEntered = false;
            }
            if (Hp <= 0)
            {
                if (CurrentBState == ShipBattleState.Entering)
                {
                    SoundManager.StopAmb("board");
                }
                CurrentBState = ShipBattleState.Idle;
            }
            if (CurrentBState == ShipBattleState.Idle)
            {
                if (TargetShip != null)
                {
                    TargetShip.IsEntered = false;
                    SoundManager.StopAmb("board");
                }
                TargetShip = null;
            }
            if (TargetShip != null && TargetShip.Owned == Owned)
            {
                CurrentBState = ShipBattleState.Idle;
                TargetShip = null;
            }

            
            else if (CurrentBState == ShipBattleState.Attacking && TargetShip != null
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
                        TargetShip.Hp -= (int)((AttackValue + AttackValueUpgrade)*0.25f);//testvalue
                        if (TargetShip.Hp <= 0)
                        {
                          Game1.mMapScreen.Drowning(TargetShip.Position, 6);
                          CurrentBState = ShipBattleState.Idle;
                          TargetShip = null;
                        }

                    }else if (TargetShip.Hp <= 0)
                    {
                        CurrentBState = ShipBattleState.Idle;
                        TargetShip = null;
                    }
                }
            }
            else if (CurrentBState == ShipBattleState.Defending && TargetShip != null && ((!TargetShip.Owned && Owned) || (!Owned && TargetShip.Owned)))
            {
                if (Vector2.Distance(Position, TargetShip.Position) <= 150f)
                {
                    Moving = false;
                    mShootingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    //if a movement command is set, the ship will only move and stop shooting
                    if (mShootingDelay <= 0 && TargetShip.Hp > 0)
                    {
                        mShootingDelay = 3f;//reset the timer
                        Game1.mMapScreen.ShootBullet(Position, TargetShip.Position);
                        TargetShip.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);//testvalue
                        if (TargetShip.Hp <= 0)
                        {
                            Game1.mMapScreen.Drowning(TargetShip.Position, 6);
                            //go to the defending position
                            if (ShipPath != null &&!ShipPath.Finished)
                            {
                                Moving = true;
                            }
                            TargetShip = null;
                        }

                   } 
                
                } else if (!Moving)
                {
                    //go to the defending position
                    if (ShipPath!= null && !ShipPath.Finished)
                    {
                      Moving = true;
                    }
                    TargetShip = null;//looks for new enemies

                }
               
            }else if (CurrentBState == ShipBattleState.Entering && TargetShip != null && ((!TargetShip.Owned && Owned) || (!Owned && TargetShip.Owned)))
            {

                if (TargetShip.Moving)
                {
                    Chasing = true;
                }
                if (Vector2.Distance(Position, TargetShip.Position) <= 60f || Chasing && Vector2.Distance(Position, TargetShip.Position) <= 70f)
                {
                    if (!Docking && !TargetShip.IsEntered)
                    {
                        SoundManager.PlayAmb("board", true);
                    }
                    Chasing = false;
                    Docking = true;
                    TargetShip.IsEntered = true;
                    Moving = false;
                    Direction = TargetShip.Direction;
                }

                //the actual fight, subtracting the Enterattackvalues until one crew is completely dead
                if (Docking && TargetShip.IsEntered)
                {
                    var tEnter = TargetShip.EnterAttackValue;
                    TargetShip.EnterAttackValue -= 0.001f + (EnterAttackValue + EnterAttackValueUpgrade)*0.0003f;
                    TargetShip.AllPiratesOnShip -= 0.001f + (EnterAttackValue + EnterAttackValueUpgrade) * 0.0003f;
                    AllPiratesOnShip -= 0.001f + tEnter * 0.0003f;
                    EnterAttackValue -= 0.001f + tEnter * 0.0003f;
                    
                    // Add Brawl Animations.
                    Game1.mMapScreen.Brawl(TargetShip.Position, 6f);

                    //this ship lost
                    
                    if (EnterAttackValue <= 0 )
                    {
                        CurrentBState = ShipBattleState.Idle;
                        TargetShip.IsEntered = false;
                        IsEntered = false;
                        Owned = !Owned;
                        mShipTexture = Game1.mContentManager.Load<Texture2D>(Owned
                            ? "Ships/battle_ship_texture"
                            : "Ships/enemy_ship_texture");

                        if (EnterAttackValue < 0)
                        {
                            AllPiratesOnShip += (EnterAttackValue*-1);
                        }
                        EnterAttackValue = 5f;
                        AllPiratesOnShip += 5f;
                        TargetShip.AllPiratesOnShip += (TargetShip.EnterAttackValue - (int)TargetShip.EnterAttackValue);
                        SoundManager.StopAmb("board");
                        Docking = false;
                       

                    }
                    else if (TargetShip.EnterAttackValue <= 0 || TargetShip.Hp <= 0 && TargetShip != null)// the other ship lost
                    {
                        TargetShip.Owned = !TargetShip.Owned;
                        TargetShip.IsEntered = false;
                        var battleShip = TargetShip as BattleShip;
                        if (battleShip?.TargetShip != null)
                        {
                            battleShip.TargetShip.IsEntered = false;
                            TargetShip.mShipTexture = Game1.mContentManager.Load<Texture2D>(Owned
                            ? "Ships/battle_ship_texture"
                            : "Ships/enemy_ship_texture");
                        }
                        IsEntered = false;
                        //reset all actions of the newly gained ship
                        var ship = TargetShip as BattleShip;
                        if (ship != null)
                        {
                            var tShip = ship;
                            tShip.CurrentBState = ShipBattleState.Idle;
                            
                        }else if (TargetShip is TradingShip)
                        {
                            var tShip = (TradingShip) TargetShip;
                            tShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                        }
                        CurrentBState = ShipBattleState.Idle;
                        
                       

                        TargetShip.HealthBar = null;
                        TargetShip.CrewBar = null;
                        
                        if (TargetShip.EnterAttackValue < 0)
                        {
                            TargetShip.AllPiratesOnShip += (TargetShip.EnterAttackValue*-1);//add the missing number to "0" enterattackvalue
                        }
                        TargetShip.EnterAttackValue = 5f;
                        TargetShip.AllPiratesOnShip += 5f;
                        AllPiratesOnShip += ( EnterAttackValue - (int)EnterAttackValue);
                        SoundManager.StopAmb("board");
                        SoundManager.PlayEfx("efx/Triumph");
                        Docking = false;
                    }
                }
            }
        }

        public override void DropLoot()
        {
            var random = new Random();
            RessourceManager.AddRessource("wood", random.Next(3, 10));
            RessourceManager.AddRessource("gold", random.Next(2, 4));
            RessourceManager.AddRessource("rum", random.Next(1, 2));
            //if (random.Next(0, 1) == 1 )// 50% dropchance
            //{
            //    RessourceManager.AddRessource("mapParts", 1);
            //}
            if (random.Next(0, 3) == 1 )// 33% dropchance
            {
                RessourceManager.AddRessource("mapParts", 1);
            }
            //RessourceManager.AddRessource("mapParts", 2);
        }

        public void Attack(AShip targetShip)
        {
            TargetShip = targetShip;
            CurrentBState = ShipBattleState.Attacking;
        }

        public void Defend(Path target)
        {
            Move(target);
            CurrentBState = ShipBattleState.Defending;
        }

        public void Enter(AShip targetShip)
        {
            TargetShip = targetShip;
            CurrentBState = ShipBattleState.Entering;
        }
    }
}
