using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using pirates.Managers;
using System.Runtime.Serialization;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Class for FisherShips. Has only movement functionality.
    /// </summary>
    public sealed class FisherShip : AShip
    {
        /// <summary>
        ///  Indicates if the FisherShip has already fished. Used for Ai.
        /// </summary>
        [DataMember]
        public bool Fished { get; set; }

        public FisherShip(Vector2 position) : base(position)
        {
            Initialize();
        }

        // ReSharper disable once UnusedMember.Global (needed for Xml Serialization.)
        public FisherShip()
        {
        }

        /// <summary>
        ///  Sets the standartvalues for the Fishership.
        /// </summary>
        public override void Initialize()
        {
            MaxHp = 30;
            Hp = (int) MaxHp;
            MaxFreePirates = 10;
            AttackValue = 0;
            EnterAttackValue = 10;
            RepairingValue = 0;
            MovementSpeed = 0.13f;
            InitialMovingSpeed = 0.13f;
            AllPiratesOnShip = 10;
        }

        /// <summary>
        ///  Drops the loot for the FisherShip.
        /// </summary>
        public override void DropLoot()
        {
            var random = new Random();
            var number = random.Next(1,3);
            RessourceManager.AddRessource("wood", number);
            number = random.Next(1, 3);
            RessourceManager.AddRessource("gold", number);
            //RessourceManager.AddRessource("mapParts", 1);
        }

        public override void LoadContent(ContentManager content)
        {
            mShipTexture = content.Load<Texture2D>("Ships/fisher_ship_texture");
        }
    }
}
