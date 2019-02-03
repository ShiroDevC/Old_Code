using System;
using System.Xml.Serialization;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.AI.Pathfinding;
using pirates.Managers;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Class for TradingShips. Adds a limited Battlefunctionality to AShip.
    /// </summary>
    public sealed class TradingShip : AShip, IBattleObject, IUpdatableObject
    {

        /// <summary>
        ///  Enum for the different Battlestates the Ship can be in.
        /// </summary>
        // ReSharper disable once UnusedMember.Local
        // ReSharper disable once UnusedMember.Local
        // ReSharper disable once UnusedMember.Local
        // ReSharper disable once UnusedMember.Local
        [XmlType(TypeName = "TradingShipShipBattleState", AnonymousType = true)]
        public enum ShipBattleState { Attacking, Defending, Idle}

        /// <summary>
        ///  Instance of the BattleState enum. To be used at the Updateloop.
        /// </summary>
        public ShipBattleState CurrentBState { get; set; }

        public AShip TargetShip { get; set; }

        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        public bool Chasing { get; private set; }

        private double mShootingDelay;

        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="position"></param>
        public TradingShip(Vector2 position) : base(position)
        {
            Initialize();
        }

        // ReSharper disable once UnusedMember.Global
        // ReSharper disable once RedundantBaseConstructorCall
        public TradingShip() : base()
        {
        }

        /// <summary>
        ///  Sets the specific attributes of TradingShips.
        /// </summary>
        public override void Initialize()
        {
            CurrentBState = ShipBattleState.Idle;
            MaxHp = 80;
            Hp = (int) MaxHp;
            MaxFreePirates = 25;
            AttackValue = 10;
            EnterAttackValue = 10;
            RepairingValue = 0;
            MovementSpeed = 0.15f;
            InitialMovingSpeed = 0.15f;
            AllPiratesOnShip = 20;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/TradeShip");
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

        public void Update(GameTime gameTime)
        {
            if (Hp <= 0)
            {
                CurrentBState = ShipBattleState.Idle; 
            }
            if (CurrentBState == ShipBattleState.Idle && TargetShip != null)
            {
                TargetShip = null;

            }
            if (TargetShip != null && TargetShip.Owned == Owned)
            {
                CurrentBState = ShipBattleState.Idle;
                TargetShip = null;
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

                    mShootingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    if (mShootingDelay <= 0 && TargetShip.Hp > 0)
                    {
                        Game1.mMapScreen.ShootBullet(Position, TargetShip.Position);
                        mShootingDelay = 4f;//reset the timer
                        TargetShip.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);//testvalue
                        if (TargetShip.Hp <= 0)
                        {
                            Game1.mMapScreen.Drowning(TargetShip.Position, 6);
                            CurrentBState = ShipBattleState.Idle;
                        }

                    }
                    else if (TargetShip.Hp <= 0)
                    {
                        CurrentBState = ShipBattleState.Idle;
                        TargetShip = null;
                    }
                }

            }
            else if (CurrentBState == ShipBattleState.Defending && TargetShip != null
                && ((!TargetShip.Owned && Owned) || (!Owned && TargetShip.Owned)))
            {
                if (Vector2.Distance(Position, TargetShip.Position) <= 150f)
                {
                    Moving = false;
                    mShootingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    //if a movement command is set, the ship will only move and stop shooting
                    if (mShootingDelay <= 0 && TargetShip.Hp > 0)
                    {
                        Game1.mMapScreen.ShootBullet(Position, TargetShip.Position);
                        mShootingDelay = 3f;//reset the timer
                        TargetShip.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);//testvalue
                        if (TargetShip.Hp <= 0)
                        {
                            Game1.mMapScreen.Drowning(TargetShip.Position, 6);
                            //go to the defending position
                            if (!ShipPath.Finished)
                            {
                                Moving = true;
                            }
                            TargetShip = null;
                        }

                    }

                }
                else if (!Moving)
                {
                    //go to the defending position
                    if (!ShipPath.Finished)
                    {
                        Moving = true;
                    }
                    TargetShip = null;//looks for new enemies

                }

            }
        }

        public override void DropLoot()
        {
            var random = new Random();
            var number = random.Next(1, 5);
            RessourceManager.AddRessource("wood", number);
            number = random.Next(4, 16);
            RessourceManager.AddRessource("gold", number);
            number = random.Next(0, 1);
            RessourceManager.AddRessource("rum", number);
            if (random.Next(0, 5) == 2)// dropchance
            {
                RessourceManager.AddRessource("mapParts", 1);
            }
        }
    }
}
