using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.Managers;
using System.Runtime.Serialization;

namespace pirates.GameObjects
{
    public sealed class Octopus : AShip, IUpdatableObject
    {
        /// <summary>
        ///  Enum for the different Battlestates the Ship can be in.
        /// </summary>
        public enum ShipBattleState { Entering, Idle }

        /// <summary>
        ///  Instance of the BattleState enum. To be used at the Updateloop.
        /// </summary>
        // ReSharper disable once UnusedAutoPropertyAccessor.Global
        [DataMember]
        public ShipBattleState CurrentBState { get; private set; }

        [DataMember]
        public AShip TargetShip { get; set; }
        [DataMember]
        public bool Docking { get; set; }

        [DataMember]
        public Vector2 HousingPosition { get; set; }

        [DataMember]
        private double EnterRegenerationDelay { get; set; }


        public Octopus(Vector2 position) : base(position)
        {
            Initialize();
        }

        // ReSharper disable once UnusedMember.Global (needed for Xml Serialization.)
        public Octopus()
        {
            
        }

        public override void Initialize()
        {
            CurrentBState = ShipBattleState.Idle;
            HousingPosition = Position;
            MaxHp = 200;
            Hp = (int)MaxHp;
            MaxFreePirates = 80;
            AttackValue = 0;
            EnterAttackValue = 30f;
            RepairingValue = 0;
            MovementSpeed = 0.35f;
            InitialMovingSpeed = 0.35f;
            AllPiratesOnShip = 30;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/octopusprite");
        }

        public void Update(GameTime gameTime)
        {
            if (CurrentBState != ShipBattleState.Entering && Docking)
            {
                SoundManager.StopAmb("board");
                Docking = false;
                if (TargetShip != null) TargetShip.IsEntered = false;
            }
           
            if (TargetShip != null && CurrentBState == ShipBattleState.Entering && TargetShip.Owned)
            {
                EnterRegenerationDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                if (EnterRegenerationDelay <= 0 && EnterAttackValue < 30)
                {
                    EnterRegenerationDelay = 10;
                    EnterAttackValue = 30;
                    AllPiratesOnShip = 30;
                }
                if (Vector2.Distance(Position, TargetShip.Position) <= 70f)
                {
                    if (!Docking && !TargetShip.IsEntered && Hp >= 0)
                    {
                        SoundManager.PlayAmb("board", true);
                    }
                    Docking = true;
                    TargetShip.IsEntered = true;
                    Moving = false;
                    Direction = TargetShip.Direction;
                }

                //the actual fight, subtracting the Enterattackvalues until one crew is completely dead
                if (Docking && TargetShip.IsEntered)
                {
                    var tEnter = TargetShip.EnterAttackValue;
                    TargetShip.EnterAttackValue -= 0.001f + (EnterAttackValue + EnterAttackValueUpgrade) * 0.0003f;
                    EnterAttackValue -= 0.001f + tEnter * 0.0003f;

                    // Add Brawl Animations.
                    Game1.mMapScreen.Brawl(TargetShip.Position, 6f);

                    //the Octopus can't be entered
                    if (Hp <= 0)
                    {
                        TargetShip.IsEntered = false;
                        CurrentBState = ShipBattleState.Idle;
                        Docking = false;
                        SoundManager.StopAmb("board");
                    }
                    else if (TargetShip.EnterAttackValue <= 0 || TargetShip.Hp <= 0 && TargetShip != null)
                    {
                        TargetShip.Hp = 0;
                        Docking = false;
                        CurrentBState = ShipBattleState.Idle;
                        SoundManager.StopAmb("board");
                    }
                }
            }
        
        }

        public void Enter(AShip ship)
        {
            CurrentBState = ShipBattleState.Entering;
            TargetShip = ship;
        }

        public override void DropLoot()
        {
            var random = new Random();
            var number = random.Next(10, 30);
            RessourceManager.AddRessource("wood", number);
            number = random.Next(200, 300);
            RessourceManager.AddRessource("gold", number);
            RessourceManager.AddRessource("mapParts", 1);
        }
    }
}
