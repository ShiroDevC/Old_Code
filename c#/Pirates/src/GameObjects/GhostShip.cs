using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.Managers;
using System.Runtime.Serialization;

namespace pirates.GameObjects
{
    public sealed class GhostShip: AShip, IUpdatableObject
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
        public List<AShip> TargetShips { get; private set; }
        [DataMember]
        public AShip NearestTarget { get; private set; }
        [DataMember]
        public Vector2 TreasureIslandPosition { get; private set; }

        [DataMember]
        public bool MoveRight { get; set; }

        [DataMember]
        private double mShootingDelay = 2;

        [DataMember]
        private double mRegenerationDelay = 60;

        public GhostShip(Vector2 position) : base(position)
        {
            Initialize();
            TargetShips = new List<AShip>();
            TreasureIslandPosition = position;
        }

        // ReSharper disable once RedundantBaseConstructorCall
        public GhostShip() : base()
        {

        }

        public override void Initialize()
        {
            CurrentBState = ShipBattleState.Idle;
            MaxHp = 180;
            Hp = (int)MaxHp;
            MaxFreePirates = 180;
            AttackValue = 50;
            EnterAttackValue = 100f;
            RepairingValue = 0;
            MovementSpeed = 0.275f;
            InitialMovingSpeed = 0.275f;
            AllPiratesOnShip = 150;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/ghostship");
        }
        
        public void Attack(List<AShip> targets)
        {
            CurrentBState = ShipBattleState.Attacking;
            TargetShips = targets;//assumes that only owned ships will be in the list.
            NearestTarget = TargetShips[0];

        }



        public void Update(GameTime gameTime)
        {
            if (Owned)
            {
                Hp = 0;//self destruction
            }
            if (Hp <= 0)
            {
                CurrentBState = ShipBattleState.Idle;
            }
            if (CurrentBState == ShipBattleState.Attacking && TargetShips != null)
            {
                //look if the Hp should be refilled.
                mRegenerationDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                if (mRegenerationDelay <= 0 && Hp < MaxHp)
                {
                    Hp = MaxHp;
                    mRegenerationDelay = 60;
                }

                //firing 
                var fireCounter = 3;//fire to the max of 3 ships simultaniously
                if (TargetShips.Count < 3)fireCounter = TargetShips.Count;

                //to count how many ships where shot at this firing intervall
                //check if any TargetShip is in reach, saves the closest one
                var counter = TargetShips.Count;
                mShootingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                for(var i = 0; i < counter; i++)
                {
                    var ship = TargetShips[i];
                    var distance = Vector2.Distance(ship.Position, Position);
                    fireCounter--;
                    if (distance <= 150)
                    {
                        
                        if (ship.Hp > 0 && mShootingDelay <= 0 )
                        {
                            Game1.mMapScreen.ShootBullet(Position, ship.Position);
                            
                            ship.Hp -= (int)((AttackValue + AttackValueUpgrade) * 0.25f);//testvalue
                            

                           
                           
                        }
                    //don't chase too much    
                    }else if (distance >= 400)
                    {
                        TargetShips.Remove(ship);
                        counter--;
                    }

                    if (mShootingDelay <= 0 && fireCounter <= 0)
                    {
                        mShootingDelay = 3f;//reset the timer
                        break;
                    }

                    if (ship.Hp <= 0 || !ship.Owned)
                    {
                         TargetShips.Remove(ship);
                         counter--;
                         if (TargetShips.Count <= 0)
                         {
                              CurrentBState = ShipBattleState.Idle;
                              NearestTarget = null;
                          }
                    }

                    
                    //refresh the closest enemyShip.
                    if (NearestTarget != null && Vector2.Distance(NearestTarget.Position, Position) < distance)
                    {
                        NearestTarget = ship;
                    }
                    
                }
                
                
            }else if (TargetShips != null && (CurrentBState == ShipBattleState.Attacking && TargetShips.Count <= 0))
            {
                CurrentBState = ShipBattleState.Idle;
                NearestTarget = null;

            }
        }

        public override void DropLoot()
        {
            var random = new Random();
            var number = random.Next(20, 100);
            RessourceManager.AddRessource("wood", number);
            number = random.Next(200, 800);
            RessourceManager.AddRessource("gold", number);
            number = random.Next(5, 10);
            RessourceManager.AddRessource("rum", number);

        }


    }
}
