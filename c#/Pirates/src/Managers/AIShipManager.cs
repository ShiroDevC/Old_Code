using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using MonoGame.Extended;
using MonoGame.Extended.Shapes;
using pirates.GameObjects;

namespace pirates.Managers
{
    public sealed class AiShipManager : ShipManager
    {
        /// <summary>
        ///  All ships controlled by the AI.
        /// </summary>
        private List<BattleShip> mAiBattleShipsList = new List<BattleShip>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        // ReSharper disable once UnusedMember.Global
        public List<BattleShip> AiBattleShips
        {
            get { return mAiBattleShipsList; }
            set { mAiBattleShipsList = value; }
        }

        /// <summary>
        ///  All TradingShips(currently Trading).
        /// </summary>
        private List<TradingShip> mAiTradingShipList = new List<TradingShip>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        // ReSharper disable once UnusedMember.Global
        public List<TradingShip> AiTradingShips
        {
            get { return mAiTradingShipList; }
            set { mAiTradingShipList = value; }
        }

        /// <summary>
        ///  All FisherShips
        /// </summary>
        private List<FisherShip> mAiFisherShipList = new List<FisherShip>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        // ReSharper disable once UnusedMember.Global
        public List<FisherShip> AiFisherShips
        {
            get { return mAiFisherShipList; }
            set { mAiFisherShipList = value; }
        }

        /// <summary>
        ///  All Fleets controlled by the AI.
        /// </summary>
        private List<Fleet> mAiFleetList = new List<Fleet>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        // ReSharper disable once UnusedMember.Global
        public List<Fleet> AiFleets
        {
            get { return mAiFleetList; }
            set { mAiFleetList = value; }
        }

        public GhostShip GhostShip { get; private set; }

        public  Octopus Octopus { get; private set; }

        public Dragon Dragon { get; private set; }

        public Fleet AdmiralsFleet { get; private set; }

        private double mTradingMovingDelay;

        private double mBattleMovingDelay;

        private double mFishingMovingDelay;

        private double mGhostMovementDelay;

        private double mOctopusChasingDelay;

        private readonly List<Vector2> mFleetSpawnPoints;

        // ReSharper disable once UnusedMember.Global
        public AiShipManager()
        {
        }

        public AiShipManager(List<AShip> allShips,
            List<IBattleObject> attackingShips,
            List<IBattleObject> defendingShips,
            List<AShip> repairingShips,
            List<BattleShip> enteringShips)
        {
            mAllShipList = allShips;
            mAttackingShipList = attackingShips;
            mDefendingShipList = defendingShips;
            mRepairingShipList = repairingShips;
            mEnteringShipList = enteringShips;
            mAiBattleShipsList = new List<BattleShip>();
            mAiFleetList = new List<Fleet>();
            mAiTradingShipList = new List<TradingShip>();
            mAiFisherShipList = new List<FisherShip>();
            //all SpawnPoints for the fleets
            mFleetSpawnPoints = new List<Vector2> {new Vector2(300, 2050), new Vector2(930, 3000),
                             new Vector2(2500, 3900), new Vector2(3700, 2100), new Vector2(4800, 1300)};
        }
        

        /// <summary>
        ///  Spawns all enemy ships at the start of the game. Fleets included.
        /// </summary>
        public void InitializeShips()
        {
            if (Game1.mMapScreen.mTechDemo)
            {
                LoadTechDemo();
            }

            //spawn tradingShips
            SpawnAiTradingShip(new Vector2(500, 50));
            SpawnAiTradingShip(new Vector2(350, 1000));
            SpawnAiTradingShip(new Vector2(1500, 1480));
            SpawnAiTradingShip(new Vector2(3100, 1600));
            SpawnAiTradingShip(new Vector2(900, 2800));

            SpawnAiFisherShip(new Vector2(300, 100));
            SpawnAiFisherShip(new Vector2(350, 900));
            SpawnAiFisherShip(new Vector2(1760, 2100));
            SpawnAiFisherShip(new Vector2(950, 3000));
            SpawnAiFisherShip(new Vector2(3500, 3000));
            SpawnAiFisherShip(new Vector2(5000, 1200));
            SpawnAiFisherShip(new Vector2(4000, 3500));
            SpawnAiFisherShip(new Vector2(4700, 4700));
            SpawnAiFisherShip(new Vector2(3300, 5500));
            SpawnAiFisherShip(new Vector2(1770, 5500));
            SpawnAiFisherShip(new Vector2(100, 5500));
            //SpawnGhostShip(new Vector2(330, 100));
            #if DEBUG
                //SpawnAiBattleShip(new Vector2(300, 300));
            #endif   
            //SpawnDragon(new Vector2(300,200));
        }

        /// <summary>
        /// Load 1000 Random BattleShips into the Map for the Tech Demo.
        /// </summary>
        private void LoadTechDemo()
        {
            var r = new Random();
            for (var i = 0; i < 1000; i++)
            {
                // Search for a free position in Map.
                var pos = new Point(r.Next(0, 179), r.Next(0, 179));
                var cell = Game1.mMapScreen.mGridMap.GetCell(pos);
                while (cell == null || !cell.IsWalkable)
                {
                    pos = new Point(r.Next(0, 100), r.Next(0, 100));
                    cell = Game1.mMapScreen.mGridMap.GetCell(pos);
                }

                // Spawn a BattleShip at the free position.
                if (i % 2 == 0)
                {
                    var ship = new BattleShip(cell.Position)
                    {
                        Owned = false,
                        mShipTexture = Game1.mContentManager.Load<Texture2D>("Ships/enemy_ship_texture")
                    };
                    mAllShipList.Add(ship);
                    mAiBattleShipsList.Add(ship);
                }
                else
                {
                    var bShip = new BattleShip(cell.Position) { Owned = true };
                    mAllShipList.Add(bShip);
                    //sPlayerShipsList.Add(bShip);
                }
            }
        }

        /// <summary>
        ///  Respawns enemy ships according to the fleet of the player and the number of remaining enemy ships.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        private void RespawnShips()
        {
            if(GhostShip != null)return;
            var randomNumber = new Random();
            var mapParts = RessourceManager.GetRessourceInt("mapParts");
            if (mAiFisherShipList.Count < 12)
            {
                //spawn Fisherships until there are enough
                //random position
                var spawnPosition = new Vector2(randomNumber.Next(200, 5600), randomNumber.Next(200, 5600));
                var cell = Game1.mMapScreen.mGridMap.GetCell(spawnPosition);
                if (cell.IsWalkable && !cell.Occupied && !VisibilityManager.IsVisible(spawnPosition))SpawnAiFisherShip(spawnPosition);
                
            }

            if (mAiTradingShipList.Count < 7)//static number of tradingships
            {
                //spawn
                var spawnPosition = new Vector2(randomNumber.Next(300, 5600), randomNumber.Next(300, 5600));
                var cell = Game1.mMapScreen.mGridMap.GetCell(spawnPosition);
                if (cell.IsWalkable && !cell.Occupied && !VisibilityManager.IsVisible(spawnPosition)) SpawnAiTradingShip(spawnPosition);

            }

            if (mAiBattleShipsList.Count < 2 + mapParts*3)//by collecting more mapParts, the count of battleships increases
            {
                //spawn
                var spawnPosition = new Vector2(randomNumber.Next(400, 5600), randomNumber.Next(400, 5600));
                var cell = Game1.mMapScreen.mGridMap.GetCell(spawnPosition);
                if (cell.IsWalkable && !cell.Occupied && !VisibilityManager.IsVisible(spawnPosition)) SpawnAiBattleShip(spawnPosition);

            }

            if (mAiFleetList.Count < mapParts - 2 && mAiFleetList.Count < 3)// only up to 3 fleets
            {
                //random SpawnPoint from List.
                var spawnPosition = mFleetSpawnPoints[randomNumber.Next(0, mFleetSpawnPoints.Count - 1)];
                if (mapParts < 3)
                {
                    SpawnAiFleet(spawnPosition, 2, 1);
                }
                else
                {
                    SpawnAiFleet(spawnPosition, 3, 2);//increase strength of the fleets
                }
                
            }
            
             
        }

        /// <summary>
        ///  Spawns a Fleet with the given number of ships at the specified Position.
        /// <param name="position"> The Spawnposition of the Fleet</param>
        /// <param name="battleShips"> The number of BattleShips in the Fleet</param>
        /// <param name="tradingShips"> The number of TradingShips in the Fleet</param>
        /// </summary>
        private void SpawnAiFleet(Vector2 position, int battleShips, int tradingShips)
        {
            var testFleet = new Fleet(position, battleShips, tradingShips, mEnteringShipList,
                mAttackingShipList, mDefendingShipList, mRepairingShipList);
            mAllShipList.AddRange(testFleet.BattleShips);
            mAllShipList.AddRange(testFleet.TradingShips);
            mAiFleetList.Add(testFleet);
        }

        /// <summary>
        ///  Spawns the GhostShip at the given Position
        /// </summary>
        public void SpawnGhostShip(Vector2 position)
        {
            GhostShip = new GhostShip(position);
            mAllShipList.Add(GhostShip);
            //kill the fleets
            foreach (var fleet in mAiFleetList)
            {
                if (fleet.Equals(AdmiralsFleet))
                {
                    continue;
                }
                //fleet.Defending = true;//stops movement of all fleets
                foreach (var bShip in fleet.BattleShips)
                {
                    mAllShipList.Remove(bShip);
                    bShip.Hp = 0;//kill all battleships
                }
                foreach (var tShip in fleet.TradingShips)
                {
                    mAllShipList.Remove(tShip);
                    tShip.Hp = 0;//kill all tradingShips
                }
            }
            foreach (var bShip in AiBattleShips)
            {
                mAllShipList.Remove(bShip);
                bShip.Hp = 0;
            }
            foreach (var tShip in AiTradingShips)
            {
                mAllShipList.Remove(tShip);
                tShip.Hp = 0;
            }

        }

        /// <summary>
        ///  Spawns the GhostShip at the given Position
        /// </summary>
        public void SpawnDragon(Vector2 position)
        {
            Dragon = new Dragon(position);
            mAllShipList.Add(Dragon);
        }

        /// <summary>
        ///  Spawns the Octopus at the given Position
        /// </summary>
        public void SpawnOctopus(Vector2 position)
        {
            Octopus = new Octopus(position);
            mAllShipList.Add(Octopus);
        }

        /// <summary>
        ///  Spawns the the Fleet to kill in the quest.
        /// </summary>
        public void SpawnAdmiralsFleet(Vector2 position)
        {
            AdmiralsFleet = new Fleet(position, 3, 2, mEnteringShipList,
                mAttackingShipList, mDefendingShipList, mRepairingShipList) {Defending = true};
            mAllShipList.AddRange(AdmiralsFleet.BattleShips);
            mAllShipList.AddRange(AdmiralsFleet.TradingShips);
            mAiFleetList.Add(AdmiralsFleet);
        }

        /// <summary>
        ///  Spawns a Battleship at the given position, owned by the ai.
        /// </summary>
        internal void SpawnAiBattleShip(Vector2 position)
        {
            var aiBShip = new BattleShip(position)
            {
                Owned = false,
                mShipTexture = Game1.mContentManager.Load<Texture2D>("Ships/enemy_ship_texture")
            };

            mAllShipList.Add(aiBShip);
            mAiBattleShipsList.Add(aiBShip);
        }

        /// <summary>
        ///   Spawns a Tradingship at the given position, owned by the ai.
        /// </summary>
        private void SpawnAiTradingShip(Vector2 position)
        {
            var aiTShip = new TradingShip(position) { Owned = false };
            mAllShipList.Add(aiTShip);
            mAiTradingShipList.Add(aiTShip);
        }

        /// <summary>
        ///   Spawns a Fishership at the given position, owned by the ai.
        /// </summary>
        // ReSharper disable once UnusedMember.Local
        private void SpawnAiFisherShip(Vector2 position)
        {
            var aiFShip = new FisherShip(position) { Owned = false };
            mAllShipList.Add(aiFShip);
            mAiFisherShipList.Add(aiFShip);
        }

        private AShip SearchClosestShip(AShip ship,QuadTree quadTree, float range)
        {
            var possibleCollisions = new List<AShip>();
            quadTree.Retrieve(possibleCollisions, ship);
            AShip nearestShip = null;
            foreach (var potentialEnemyShip in possibleCollisions)
            {
                //only add ships that are new
                var rangeCircle = new CircleF(ship.Position, range); //scan radius
                if (rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                     potentialEnemyShip.Hp >= 0)
                {
                    if (nearestShip == null)
                    {
                        nearestShip = potentialEnemyShip;
                    }
                    else if (Vector2.Distance(nearestShip.Position, ship.Position) > Vector2.Distance(potentialEnemyShip.Position, ship.Position))
                    {
                        nearestShip = potentialEnemyShip;
                    }
                }
            }
            return nearestShip;
        }
        /// <summary>
        ///  Check for possible actions for the Fleets and single Ships controled by the AI.
        /// </summary>
        public void Update(GameTime gameTime, QuadTree quadTree)
        {
            

            //FisherShips
            var counter = mAiFisherShipList.Count;
            for (var i = 0; i < counter; i++)
            {
                var fShip = mAiFisherShipList[i];
                if (!fShip.Moving)
                {
                    if (mFishingMovingDelay <= 0)
                    {
                        var randomNumber = new Random();
                        //moving to a random position in the Map
                        var x = randomNumber.Next(0, 5760);
                        var y = randomNumber.Next(0, 5760);
                        fShip.Move(PathFinder.CalculatePath(fShip.Position, new Vector2(x, y), false));
                        mFishingMovingDelay = 8;
                        
                    }
                    else
                    {
                        mFishingMovingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    }
                    
                }
                if (!fShip.Owned && fShip.Hp > 0) continue;
                mAiFisherShipList.RemoveAt(i);
                counter--;
                fShip.HealthBar = null;
                fShip.CrewBar = null;
                if (fShip.Owned
                    ) { Game1.mEventScreen.mEventManager.UpdateStatTotal("Ships Hijacked", 1);}
            }
            
            //TradingShips
            counter = mAiTradingShipList.Count;
            for (var i = 0; i < counter; i++)
            {
                var tShip = mAiTradingShipList[i];
                if (!tShip.Moving)
                {
                    if (mTradingMovingDelay <= 0)
                    {
                        var randomNumber = new Random();
                        var number = randomNumber.Next(0, IslandManager.IslandCount);
                        var destination = new Vector2(IslandManager.Islands[IslandManager.mIslandNames[number]].X + randomNumber.Next(20, 50),
                            IslandManager.Islands[IslandManager.mIslandNames[number]].Y+ randomNumber.Next(20, 50));
                        if (Vector2.Distance(destination, tShip.Position) > 100 
                            && Game1.mMapScreen.mGridMap.GetCell(destination).IsWalkable 
                            && !Game1.mMapScreen.mGridMap.GetCell(destination).Occupied)
                        {
                            tShip.Move(PathFinder.CalculatePath(tShip.Position, destination, false));
                            mTradingMovingDelay = 5;
                        }
                        
                    }
                    else
                    {
                        mTradingMovingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    }

                }

                if (tShip.Hp < tShip.MaxHp) //shoot back
                {
                    if (!mDefendingShipList.Contains(tShip))
                    {
                        tShip.Defend(tShip.ShipPath);
                        mDefendingShipList.Add(tShip);
                    }
                    if (tShip.Hp <= 40) //fleeing
                    {
                        tShip.TargetShip = null;
                        tShip.Move(tShip.ShipPath);
                        tShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                        mDefendingShipList.Remove(tShip);
                    }

                }

                if (!tShip.Owned && tShip.Hp > 0) continue;
                mAiTradingShipList.RemoveAt(i);
                counter--;
                if (tShip.Owned)
                {
                    tShip.CrewBar = null;
                    tShip.HealthBar = null;
                    Game1.mEventScreen.mEventManager.UpdateStatTotal("Ships Hijacked",1);
                    var random = new Random();
                    if (random.Next(0, 4) == 1)// 25% dropchance
                    {
                        RessourceManager.AddRessource("mapParts", 1);
                    }
                }
            }


            //BattleShips
            counter = mAiBattleShipsList.Count;
            for (var i = 0; i < counter; i++)
            {
                var bShip = mAiBattleShipsList[i];
                if (bShip.CurrentBState == BattleShip.ShipBattleState.Idle)
                {
                    if (!bShip.Moving)
                    {
                        if (mBattleMovingDelay <= 0)
                        {
                            //moving to a random position in the Map
                            var randomNumber = new Random();
                            var x = randomNumber.Next(0, 5760);
                            var y = randomNumber.Next(0, 5760);
                            bShip.Move(PathFinder.CalculatePath(bShip.Position, new Vector2(x, y), false));
                            mBattleMovingDelay = 3;
                        }
                        else
                        {
                            mBattleMovingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                        }
                    }

                    //scan for possible enemies in reach and attack them if they aren't to powefull
                    var possibleCollisions = new List<AShip>();
                    var enemyShipsCount = 0;
                    quadTree.Retrieve(possibleCollisions, bShip);
                    if (possibleCollisions.Count > 0)
                    {
                        AShip nearestShip = null;
                        for (var index = 0; index < possibleCollisions.Count; index++)
                        {

                            var rangeCircle = new CircleF(bShip.Position, 500f); //scan radius
                            if (rangeCircle.Contains(possibleCollisions[index].Position) &&
                                possibleCollisions[index].Owned && possibleCollisions[index].Hp >= 0)
                            {
                                if (nearestShip == null)
                                {
                                    nearestShip = possibleCollisions[index];
                                }
                                enemyShipsCount++;
                                //save the nearest Ship
                                if (Vector2.Distance(bShip.Position, possibleCollisions[index].Position) <
                                    Vector2.Distance(bShip.Position, nearestShip.Position))
                                {
                                    nearestShip = possibleCollisions[index];
                                }

                            }

                        }
                        //only attack up to 3 ships
                        if (enemyShipsCount > 0 && enemyShipsCount <= 3 && nearestShip != null)
                        {
                            var random = new Random();
                            var number = random.Next(0, 2);
                            if ((number == 1) && nearestShip.EnterAttackValue -8 < bShip.EnterAttackValue)
                            {
                                bShip.Move(PathFinder.CalculatePath(bShip.Position, nearestShip.Position, false));
                                bShip.Enter(nearestShip);
                                mEnteringShipList.Add(bShip);
                            }
                            else
                            {
                                bShip.Move(PathFinder.CalculatePath(bShip.Position, nearestShip.Position, false));
                                bShip.Attack(nearestShip);
                                mAttackingShipList.Add(bShip);
                            }
                        }
                        else if (enemyShipsCount > 3)
                        {
                            bShip.CurrentBState = BattleShip.ShipBattleState.Defending;
                            mDefendingShipList.Add(bShip);
                        }
                    }
                }

                if (!bShip.Owned && bShip.Hp > 0) continue;
                mAiBattleShipsList.RemoveAt(i);
                counter--;
                bShip.CrewBar = null;
                bShip.HealthBar = null;
                if (!Game1.mMapScreen.mTechDemo && bShip.Owned)
                {
                    
                    Game1.mEventScreen.mEventManager.UpdateStatTotal("Ships Hijacked", 1);
                    var random = new Random();
                    if (random.Next(0, 3) == 1)// 33% dropchance
                    {
                        RessourceManager.AddRessource("mapParts", 1);
                    }
                }
            }

            //Fleets 
            counter = mAiFleetList.Count;
            for (var t = 0; t < counter; t++)
            {
                var fleet = mAiFleetList[t];
                //check if the ships are still in the fleet
                var bCounter = fleet.BattleShips.Count;
                for (var i = 0; i < bCounter; i++)
                {
                    if (!(fleet.BattleShips[i].Hp <= 0) && !fleet.BattleShips[i].Owned) continue;
                    fleet.BattleShips.RemoveAt(i);
                    bCounter--;
                }
                var tCounter = fleet.TradingShips.Count;
                for (var i = 0; i < tCounter; i++)
                {
                    if (!(fleet.TradingShips[i].Hp <= 0) && !fleet.TradingShips[i].Owned) continue;
                    fleet.TradingShips.RemoveAt(i);
                    tCounter--;
                }

                //ceck if fleets are whiped out
                if (fleet.FleetCount() <= 0)
                {
                    mAiFleetList.Remove(fleet);
                    counter--;
                }


                if (!fleet.InBattle)
                {  
                   //search for enemies when not in Battle
                   var possibleCollisions = new List<AShip>();
                   var toAttack = new List<AShip>();
                   quadTree.Retrieve(possibleCollisions, fleet.FlagShip);
                   //check if the ships are enemies and in range 
                   foreach (var potentialEnemyShip in possibleCollisions)
                   {
                       var rangeCircle = new CircleF(fleet.FlagShip.Position, 600f); //scan radius
                       if (rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                            potentialEnemyShip.Hp >= 0)
                       {
                           toAttack.Add(potentialEnemyShip);
                       }
                   }
                   //if there are any enemies, attack them
                   if (toAttack.Count > 0)
                   {
                       fleet.Attack(toAttack);
                   }

                    //random movement. Determines with the Flagship if the fleet is moving.
                    if (!fleet.FlagShip.Moving && !fleet.Defending)
                    {
                        if (mBattleMovingDelay <= 0)
                        {
                            //moving to a random position in the Map
                            var randomNumber = new Random();
                            var x = randomNumber.Next(0, 5760);
                            var y = randomNumber.Next(0, 5760);
                            fleet.Move(new Vector2(x, y));
                            mBattleMovingDelay = 3;
                        }
                        else
                        {
                            mBattleMovingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                        }
                    }
                }
                else//when in battle
                {
                    //check if own ships were entered
                    for (int i = 0; i < fleet.BattleShips.Count; i++)
                    {
                        if (fleet.BattleShips[i].Owned)
                        {
                            fleet.MarkedShips.Add(fleet.BattleShips[i]);
                            fleet.BattleShips.RemoveAt(i);
                        }
                    }
                    //check if own ships were entered
                    for (int i = 0; i < fleet.TradingShips.Count; i++)
                    {
                        if (fleet.TradingShips[i].Owned)
                        {
                            fleet.MarkedShips.Add(fleet.TradingShips[i]);
                            fleet.TradingShips.RemoveAt(i);
                        }
                    }


                    //check if the marked ships still exist and the distance
                    var kCounter = fleet.MarkedShips.Count;
                    for(var i = 0; i < kCounter; i++)
                    {
                        if (fleet.MarkedShips[i].Hp <= 0 || !fleet.MarkedShips[i].Owned || Vector2.Distance(fleet.MarkedShips[i].Position, fleet.FlagShip.Position) > 600)
                        {
                            fleet.MarkedShips.RemoveAt(i);
                            kCounter--;
                            i--;
                        }
                    }
                    
                    fleet.UpdateBattle();
                    //check for enemies
                    var possibleCollisions = new List<AShip>();
                    var toAttack = new List<AShip>();
                    quadTree.Retrieve(possibleCollisions, fleet.FlagShip);
                    foreach (var potentialEnemyShip in possibleCollisions)
                    {
                        //only add ships that are new
                        var rangeCircle = new CircleF(fleet.FlagShip.Position, 700f); //scan radius
                        if (!fleet.MarkedShips.Contains(potentialEnemyShip) && rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                             potentialEnemyShip.Hp >= 0)
                        {
                            toAttack.Add(potentialEnemyShip);
                        }
                    }
                    if (toAttack.Count > 0)
                    {
                        fleet.MarkedShips.AddRange(toAttack);
                    }


                    //if there is no enemy left, the fleet will stop battling
                    if (fleet.MarkedShips.Count <= 0)
                    {
                        fleet.InBattle = false;
                        fleet.StopBattle();
                    }
                }
                
            }

            //GhostShip
            if (GhostShip != null)
            {
               
                if (GhostShip.CurrentBState == GhostShip.ShipBattleState.Idle)
                {
                    //check if there are any enemyShips nearby
                    var enemyShips = new List<AShip>();
                    var possibleCollisions = new List<AShip>();
                    quadTree.Retrieve(possibleCollisions, GhostShip);
                    foreach (var potentialEnemyShip in possibleCollisions)
                    {
                        //only add ships that are new
                        var rangeCircle = new CircleF(GhostShip.Position, 600f); //scan radius
                        if (!GhostShip.TargetShips.Contains(potentialEnemyShip) && rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                             potentialEnemyShip.Hp >= 0)
                        {
                            enemyShips.Add(potentialEnemyShip);
                        }
                    }
                    if (enemyShips.Count > 0)
                    {
                        GhostShip.Attack(enemyShips);
                    }
                    //move to the island if not already next to it.
                    if (Vector2.Distance(GhostShip.Position, GhostShip.TreasureIslandPosition)>= 200 && !GhostShip.Moving)
                    {
                        GhostShip.Move(PathFinder.CalculatePath(GhostShip.Position, GhostShip.TreasureIslandPosition, true));
                    }
                    

                }
                else if (GhostShip.CurrentBState == GhostShip.ShipBattleState.Attacking)
                {
                    GhostShip.Update(gameTime);
                    //check if there are any new enemyShips nearby
                    var possibleCollisions = new List<AShip>();
                    quadTree.Retrieve(possibleCollisions, GhostShip);
                    foreach (var potentialEnemyShip in possibleCollisions)
                    {
                        //only add ships that are new
                        var rangeCircle = new CircleF(GhostShip.Position, 600f); //scan radius
                        if (!GhostShip.TargetShips.Contains(potentialEnemyShip) && rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                             potentialEnemyShip.Hp >= 0)
                        {
                            GhostShip.TargetShips.Add(potentialEnemyShip);
                        }
                    }

                    //moving
                    mGhostMovementDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    if (mGhostMovementDelay <= 0 && GhostShip.NearestTarget != null)
                    {
                        
                        Vector2 movementTarget;
                        if ( Vector2.Distance(GhostShip.NearestTarget.Position, GhostShip.Position) <= 120)
                        {
                            if (GhostShip.MoveRight)
                            {
                                 movementTarget = GhostShip.Position +
                                             (Vector2.Normalize(GhostShip.Position - GhostShip.NearestTarget.Position).PerpendicularCounterClockwise() * 100f);
                                GhostShip.MoveRight = false;
                            }
                            else
                            {
                                movementTarget = GhostShip.Position +
                                                 (Vector2.Normalize(GhostShip.Position - GhostShip.NearestTarget.Position).PerpendicularClockwise() * 100f);
                                GhostShip.MoveRight = true;
                            }
                            mGhostMovementDelay = 1.5;

                        }
                        else
                        {
                            movementTarget = GhostShip.NearestTarget.Position +
                                             Vector2.Normalize(GhostShip.Position - GhostShip.NearestTarget.Position) * 20f;
                            mGhostMovementDelay = 1;
                        }
                        GhostShip.Move(PathFinder.CalculatePath(GhostShip.Position, movementTarget, true));
                    }
                   

                }
                if (GhostShip.Hp <= 0)
                {
                    GhostShip.DropLoot();
                    mAllShipList.Remove(GhostShip);
                    GhostShip = null;
                }
            }
            else
            {
                //spawn ships if necessary
                RespawnShips();
            }

            
                

            if (Octopus != null)
            {
                //search for enemies
                if (Octopus.CurrentBState == Octopus.ShipBattleState.Idle)
                {
                    /*
                    var possibleCollisions = new List<AShip>();
                    quadTree.Retrieve(possibleCollisions, Octopus);
                    AShip nearestShip = null;
                    foreach (var potentialEnemyShip in possibleCollisions)
                    {
                        //only add ships that are new
                        
                        var rangeCircle = new CircleF(Octopus.Position, 400f); //scan radius
                        if (rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                             potentialEnemyShip.Hp >= 0)
                        {
                            if (nearestShip == null)
                            {
                                nearestShip = potentialEnemyShip;
                            }
                            else if (Vector2.Distance(nearestShip.Position, Octopus.Position) > Vector2.Distance(potentialEnemyShip.Position, Octopus.Position))
                            {
                                nearestShip = potentialEnemyShip;
                            }
                        }
                    }*/
                    var nearestShip = SearchClosestShip(Octopus, quadTree, 400f);//testing
                    if (nearestShip != null)
                    {
                        Octopus.Enter(nearestShip);//attack the closest enemy
                    }

                    //move back to original position
                    if (Vector2.Distance(Octopus.Position, Octopus.HousingPosition) >= 200 && !Octopus.Moving)
                    {
                        Octopus.Move(PathFinder.CalculatePath(Octopus.Position, Octopus.HousingPosition, true));
                    }

                }else if (Octopus.CurrentBState == Octopus.ShipBattleState.Entering)
                {
                    Octopus.Update(gameTime);
                    mOctopusChasingDelay -= gameTime.ElapsedGameTime.TotalSeconds;
                    if (Octopus.TargetShip != null && Vector2.Distance(Octopus.Position, Octopus.TargetShip.Position) >= 70 && mOctopusChasingDelay <= 0)
                    {
                        mOctopusChasingDelay = 2;
                        Octopus.Move(PathFinder.CalculatePath(Octopus.Position, Octopus.TargetShip.Position, true));
                    }
                }
                if (Octopus.Hp <= 0)
                {
                    Octopus.DropLoot();
                    mAllShipList.Remove(Octopus);
                    Octopus = null;
                }

            }

            if (Dragon != null)
            {
                Dragon.Update(gameTime, quadTree);//special Updates for the dragon..
                Dragon.UpdateDragonMovement(gameTime);

                //check if the Dragoon is fighting or not
                if (Dragon.CurrentBState == Dragon.ShipBattleState.Idle)
                {
                    if (!Dragon.Moving)
                    {
                        //moving to a random position in the Map
                        var randomNumber = new Random();
                        var x = randomNumber.Next(0, 5760);
                        var y = randomNumber.Next(0, 5760);
                        Dragon.MoveDragon(new Vector2(x, y));
                    }

                    /*
                    var possibleCollisions = new List<AShip>();
                    quadTree.Retrieve(possibleCollisions, Dragon);
                    AShip nearestShip = null;
                    foreach (var potentialEnemyShip in possibleCollisions)
                    {
                        //only add ships that are new
                        var rangeCircle = new CircleF(Octopus.Position, 200f); //scan radius
                        if (rangeCircle.Contains(potentialEnemyShip.Position) && potentialEnemyShip.Owned &&
                             potentialEnemyShip.Hp >= 0)
                        {
                            if (nearestShip == null)
                            {
                                nearestShip = potentialEnemyShip;
                            }
                            else if (Vector2.Distance(nearestShip.Position, Octopus.Position) > Vector2.Distance(potentialEnemyShip.Position, Octopus.Position))
                            {
                                nearestShip = potentialEnemyShip;
                            }
                        }
                    }*/
                    var nearestShip = SearchClosestShip(Dragon, quadTree, 200f);
                    if (nearestShip != null)
                    {
                        Dragon.Attack(nearestShip); //attack the closest enemy
                    }
                }else if (Dragon.CurrentBState == Dragon.ShipBattleState.Attacking)
                {
                    //Chasing
                    if (Dragon.TargetShip != null && Vector2.Distance(Dragon.Position, Dragon.TargetShip.Position) >= 70)
                    {
                        Dragon.MoveDragon(Dragon.TargetShip.Position);
                    }
                }


                if (Dragon.Hp <= 0)
                {
                    Dragon.DropLoot();
                    mAllShipList.Remove(Dragon);
                    Dragon = null;
                }
            }


        }
    }
}

