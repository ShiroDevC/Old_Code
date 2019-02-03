using System.Collections.Generic;
using Microsoft.Xna.Framework.Content;
using pirates.AI.Pathfinding;
using pirates.GameObjects;

namespace pirates.Managers
{
    public abstract class ShipManager
    {
        /// <summary>
        ///  The List of all Ships in the game.
        /// </summary>
        protected List<AShip> mAllShipList = new List<AShip>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> AllShips
        {
            get { return mAllShipList; }
            set { mAllShipList = value; }
        }

        /// <summary>
        ///  List of all selected ships.
        /// </summary>
        protected List<AShip> mSelectShipList;

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> SelectShipList
        {
            get { return mSelectShipList; }
            set { mSelectShipList = value; }
        }

        /// <summary>
        ///  List of all currently repairing Ships.
        /// </summary>
        protected List<AShip> mRepairingShipList;

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> RepairingShipList
        {
            get { return mRepairingShipList; }
            set { mRepairingShipList = value; }
        }

        /// <summary>
        ///  List of all currently fighting(Attacking) Ships.
        /// </summary>
        protected List<IBattleObject> mAttackingShipList;

        public List<IBattleObject> AttackingShipList
        {
            get { return mAttackingShipList; }
            set { mAttackingShipList = value; }
        }

        /// <summary>
        ///  List of all Ships in Defense Mode.
        /// </summary>
        protected List<IBattleObject> mDefendingShipList;

        protected static IslandManager IslandManager => Game1.mMapScreen.mIslandManager;

        public List<IBattleObject> DefendingShipList
        {
            get { return mDefendingShipList; }
            set { mDefendingShipList = value; }
        }

        /// <summary>
        ///  List of all Ships in Defense Mode.
        /// </summary>
        protected List<BattleShip> mEnteringShipList;

        public List<BattleShip> EnteringShipList
        {
            get { return mEnteringShipList; }
            set { mEnteringShipList = value; }
        }

        protected QuadTree mShipsQuadTree;

        /// <summary>
        ///  The ContentManager for loading Textures.
        /// </summary>
        protected ContentManager mContentManager;

        /// <summary>
        ///  PathFinder for the Movement of the Ship.
        /// </summary>
        protected PathFinder PathFinder => Game1.mMapScreen.mPathFinder;
    }
}
