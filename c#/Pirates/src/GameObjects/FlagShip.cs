using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Class for the FlagShip, a special BattleShip with minor differences.
    /// </summary>
    public sealed class FlagShip : BattleShip
    {
        /// <summary>
        ///  Integer for the visibility of the Flagship.
        /// </summary>
        public int SightValue { get; set; }

        /// <summary>
        ///  Integer for the visibility of the Flagship.
        /// </summary>
        public int SightValueToAdd { get; set; }

        // ReSharper disable once UnusedMember.Global (needed for Xml Serialization.)
        public FlagShip()
        {
        }

        public FlagShip(Vector2 position) : base(position)
        {
            Initialize();
        }

        public override void Initialize()
        {
            Owned = true;
            MaxHp = 100;
            Hp = (int)MaxHp;
            MaxFreePirates = 60;
            AttackValue = 15;
            EnterAttackValue = 15;
            RepairingValue = 10;
            SightValue = 10;
            MovementSpeed = 0.25f;
            InitialMovingSpeed = 0.25f;
            AllPiratesOnShip = 50;
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/flagship_texture");
        }
        
        public override void UpdateMoving(GameTime gameTime)
        {
            base.UpdateMoving(gameTime);
            if (mPiratesChangeDelay <= 0)
            {
                if (SightValueToAdd > 0)
                {
                    SightValue++;
                    SightValueToAdd--;
                }
            }
        }
    }
}
