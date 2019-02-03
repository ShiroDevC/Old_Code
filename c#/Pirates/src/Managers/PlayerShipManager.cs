using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using MonoGame.Extended;
using MonoGame.Extended.Shapes;
using pirates.AI.Pathfinding;
using pirates.GameObjects;
using pirates.GUI;

namespace pirates.Managers
{
    /// <summary>
    ///  Manages the Selection, Movement and Battle of the Ships. 
    ///  Processes Input for the given commands and Draws all Ships. 
    /// </summary>
    public sealed class PlayerShipManager: ShipManager
    {
        #region Properties
        /// <summary>
        ///  All ships controlled by the AI.
        /// </summary>
        private List<AShip> mPlayerShipsList;

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        // ReSharper disable once UnusedMember.Global
        public List<AShip> PlayerShips
        {
            get { return mPlayerShipsList; }
            set { mPlayerShipsList = value; }
        }

        /// <summary>
        ///  Texture for the Selectioncircle
        /// </summary>
        private Texture2D mSelectionCircle;

        /// <summary>
        ///  The positon of the Mouse. Is used for selecting and commands.
        /// </summary>
        private Vector2 mMouseInWorldPosition;

        /// <summary>
        /// Dummy Texture used for debugging
        /// </summary>
        private Texture2D mDummyTexture;

        /// <summary>
        /// Will draw the paths for ships if set to true.
        /// </summary>
        // ReSharper disable once MemberCanBePrivate.Global
        public bool DebugDrawPath { get; }

        /// <summary>
        /// The rate in seconds, in which the Path for Chasing is refreshed when entering.
        /// </summary>
        private double mEnteringRefreshRate;

        /// <summary>
        /// The rate in seconds, in which the Path for Chasing is refreshed when attacking.
        /// </summary>
        private double mAttackingRefreshRate;

        public AiShipManager mAiShipManager;


        // ReSharper disable once MemberCanBePrivate.Global needed for Savegame to work
        public FlagShip FlagShip { get; set; } = new FlagShip(new Vector2(0, 0));
    
        /// <summary>
        /// the font for the HP-Bars
        /// </summary>
        private SpriteFont mSmolFont;

        public enum ShipState { Moving, Attacking, Defending, Boarding }

        public ShipState mShipState;

        #endregion

        #region Init

        /// <summary>
        ///  Constructor for the PlayerShipManager.
        /// </summary>
        public PlayerShipManager(ContentManager content, bool debugDrawPath = false)
        {
            DebugDrawPath = debugDrawPath;
            mContentManager = content;
            mShipsQuadTree = new QuadTree(0, new Rectangle(0, 0, 5760, 5760)); //Mapsize
            mPlayerShipsList = new List<AShip>();
            AllShips = new List<AShip>();
            SelectShipList = new List<AShip>();
            EnteringShipList = new List<BattleShip>();
            AttackingShipList = new List<IBattleObject>();
            DefendingShipList = new List<IBattleObject>();
            RepairingShipList = new List<AShip>();

            mShipState = ShipState.Moving;
        }

        /// <summary>
        /// Initializes all container Objects for the Ships and Spawns some ships to start.
        /// </summary>
        public void Initialize()
        {
            LanguageManager.SetText("de", new Dictionary<string, string>()
                {
                    {"PSM_hp", "LP" }, {"PSM_crew", "Mannschafft"}
                });
            LanguageManager.SetText("en", new Dictionary<string, string>()
                {
                    {"PSM_hp", "HP" }, {"PSM_crew", "Crew"}
                });
            mSelectShipList = new List<AShip>();
            mAllShipList = new List<AShip>();
            mAttackingShipList = new List<IBattleObject>();
            mDefendingShipList = new List<IBattleObject>();
            mRepairingShipList = new List<AShip>();
            mEnteringShipList = new List<BattleShip>();

            mAiShipManager = new AiShipManager(mAllShipList, mAttackingShipList, mDefendingShipList, mRepairingShipList, mEnteringShipList); 
            mAiShipManager.InitializeShips();
            SpawnShips();
        }

        /// <summary>
        /// Loads all Textures of the Ships.
        /// </summary>
        public void LoadContent()
        {
            mSmolFont = mContentManager.Load<SpriteFont>("DebugFont");
            mSelectionCircle = mContentManager.Load<Texture2D>("TestTextures/kreis");

            mDummyTexture = new Texture2D(Game1.mScreenManager.GraphicsDevice, 1, 1);
            // ReSharper disable once RedundantExplicitArrayCreation
            mDummyTexture.SetData(new Color[] { Color.White });
        }

        #endregion

        #region Update

        /// <summary>
        ///  Calls update() on every ship. Checks for input and manages Selecting 
        /// and the execution of commands.
        /// </summary>
        public void Update(GameTime gameTime)
        {
            mShipsQuadTree.Clear();
            foreach (var ship in AllShips)
            {
                mShipsQuadTree.Insert(ship);
            }
            mAiShipManager.Update(gameTime, mShipsQuadTree);
            Game1.mMapScreen.EnvironmentManager.Update(mShipsQuadTree);


            //general update for all ships
            for (var i = 0; i < mAllShipList.Count; i++)
            {
                if (mAllShipList[i] is Dragon == false)
                {
                    mAllShipList[i].UpdateMoving(gameTime);
                }
                
                if (mAllShipList[i].Hp <= 0) // Ship is dead.
                {
                    Game1.mMapScreen.mGridMap.OccupyCell(mAllShipList[i].Position, true);
                    if (!mAllShipList[i].Owned)
                    {
                        mAllShipList[i].DropLoot();
                    }
                    if (mAllShipList[i] is TradingShip)
                    {
                        Game1.mEventScreen.mEventManager.UpdateStatTotal("Trading Ships Destroyed", 1);
                    }else if (mAllShipList[i] is FisherShip)
                    {
                        Game1.mEventScreen.mEventManager.UpdateStatTotal("Fisher Ships Destroyed", 1);
                    }
                    else if (mAllShipList[i] is BattleShip)
                    {
                        Game1.mEventScreen.mEventManager.UpdateStatTotal("War Ships Destroyed", 1);
                    }
                    mAllShipList.RemoveAt(i);
                }
            }
            
            //Check if any ships were entered by the AI
            for (var i = 0; i < mPlayerShipsList.Count; i++)
            {
                if (!mPlayerShipsList[i].Owned || mPlayerShipsList[i].Hp <= 0)
                {
                    var ship = mPlayerShipsList[i] as BattleShip;
                    if (ship != null)
                    {
                        ship.CurrentBState = BattleShip.ShipBattleState.Idle;
                        mAiShipManager.AiBattleShips.Add(ship);
                    }
                    else if (mPlayerShipsList[i] is TradingShip)
                    {
                        var tShip = (TradingShip)mPlayerShipsList[i];
                        tShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                        mAiShipManager.AiTradingShips.Add(tShip);
                    }
                    mPlayerShipsList.RemoveAt(i);
                }
            }

            if (AttackingShipList.Count > 0 || EnteringShipList.Count > 0)
            {
                //play battlemukke
                SoundManager.Play("background/BattleMusic");
            }
            else
            {
                SoundManager.Stop("background/BattleMusic");
            }

            // Call Update for every Attacking Ship
            UpdateAttackingShips(gameTime);

            //Check for enemy Ships to shoot at while defending(Only defending Ships)
            UpdateDefendingShips(gameTime);

            //Update and Pathrefreshing for Entering Ships
            UpdateEnteringShips(gameTime);

            // update for all ships repairing
            UpdateReparingShips(gameTime);
            
            /*
            // If repairingbutton is pressed in HUD set the ships to reparing state.
            if (!HudScreen.HudScreenInstance.RepairButtonPressed()) return;
            {
                foreach (var ship in mSelectShipList)
                {
                    if (!ship.Owned || mRepairingShipList.Contains(ship)) continue;
                    ship.Repairing = true;
                    mRepairingShipList.Add(ship);
                }
            }*/
        }
        #endregion

        #region add ships to lists
        /// <summary>
        /// Adds ships from selection to repair-list
        /// </summary>
        public void AddRepairingShips()
        {
            /*foreach (var ship in mSelectShipList)
            {
                if (!ship.Owned || mRepairingShipList.Contains(ship)) continue;
                ship.Repairing = true;
                mRepairingShipList.Add(ship);
            }*/

            foreach (var ship in mSelectShipList)
            {
                if (!ship.Owned) continue;
                if (mRepairingShipList.Contains(ship))
                {
                    ship.Repairing = false;
                    mRepairingShipList.Remove(ship);
                }
                else
                {
                    ship.Repairing = true;
                    mRepairingShipList.Add(ship);
                }

            }
        }

        /// <summary>
        /// Sets current selected ships in attacking state
        /// </summary>
        public void SetShipsAttacking()
        {
            int amount = 0;
            
            //check if there is a ship at the position that was clicked
            var lookupShip = new BattleShip(mMouseInWorldPosition);
            var possibleCollisions = new List<AShip>();
            mShipsQuadTree.Retrieve(possibleCollisions, lookupShip);

            foreach (var ship in possibleCollisions)
            {
                //testweise ein quadrat über die mitte des schiffs.
                var selectRange = new Rectangle((int)ship.Position.X - 20,
                    (int)ship.Position.Y - 20,
                    40,
                    40);
                if (!selectRange.Contains(mMouseInWorldPosition) || ship.Owned) continue;
                //every selected ship attacks the target ship
                foreach (var selectedShip in mSelectShipList)
                {
                    if (selectedShip.Owned && !selectedShip.IsEntered)
                    {
                        if (!(selectedShip is IBattleObject)) continue;
                        //Vector2 destinationAddition = new Vector2(0, 0);
                        /* if (mSelectShipList.IndexOf(ship) != 0)  
                        {
                            destinationAddition = Vector2.Normalize(mSelectShipList[0].Position - ship.Position) * 100;
                                            - destinationAddition -> bei move
                        }*/


                        var frontVector = Vector2.Normalize(selectedShip.Position - ship.Position);
                        Vector2 finalDestination;
                        if (mSelectShipList.IndexOf(selectedShip) % 2 == 0)
                        {
                            finalDestination = ship.Position + (frontVector * 50 + frontVector.PerpendicularClockwise() * 20 * mSelectShipList.IndexOf(selectedShip));
                        }
                        else
                        {
                            finalDestination = ship.Position + (frontVector * 50 + frontVector.PerpendicularCounterClockwise() * 20 * mSelectShipList.IndexOf(selectedShip));
                        }

                        if (Vector2.Distance(finalDestination, ship.Position) >= 150f)
                        {
                            finalDestination = Vector2.Normalize(finalDestination - ship.Position) * 70;
                        }
                        selectedShip.Move(PathFinder.CalculatePath(selectedShip.Position, finalDestination, false));

                        var attackingShip = (IBattleObject)selectedShip;
                        attackingShip.Attack(ship);
                        if (!mAttackingShipList.Contains(attackingShip))
                        {
                            mAttackingShipList.Add(attackingShip);
                        }
                        amount++;
                    }

                }
                if (amount > 0)
                    SoundManager.PlayAmb(amount > 1 ? "cmd_attack_fleet" : "cmd_attack", false);
                break; //only one ship can be attacked at a time
            }
        }

        /// <summary>
        /// Sets current selected ships in defending state
        /// </summary>
        public void SetShipsDefending()
        {
            int amount = 0;
            
            foreach (var ship in mSelectShipList)
            {
                if (ship.Owned && !ship.IsEntered)
                {
                    if (!(ship is IBattleObject)) continue;
                    Vector2 destinationAddition = new Vector2(0, 0);
                    if (mSelectShipList.IndexOf(ship) != 0)
                    {
                        destinationAddition =
                            Vector2.Normalize(mSelectShipList[0].Position - ship.Position) * 100;

                    }

                    var defendingShip = (IBattleObject)ship;
                    defendingShip.Defend(PathFinder.CalculatePath(ship.Position,
                        mMouseInWorldPosition - destinationAddition,
                        false));
                    if (!mDefendingShipList.Contains(defendingShip))
                    {
                        mDefendingShipList.Add(defendingShip);
                    }
                    amount++;
                }


            }
            if (amount > 0)
                SoundManager.PlayAmb(amount > 1 ? "cmd_defend_fleet" : "cmd_defend", false);
        }

        /// <summary>
        /// Sets current selected ships in boarding state
        /// </summary>
        public void SetShipsBoarding()
        {
            bool playSound = false;

            foreach (var ship in mAllShipList)
            {
                //testweise ein quadrat über die mitte des schiffs.
                var selectRange = new Rectangle((int)ship.Position.X - 20,
                    (int)ship.Position.Y - 20,
                    40,
                    40);
                if (!selectRange.Contains(mMouseInWorldPosition) || ship.Owned || ship is Dragon) continue;// check if the ship is a dragon(can't be entered)
                                                                                                           //every selected ship attacks the target ship
                foreach (var selectedShip in mSelectShipList)
                {
                    if (!selectedShip.Owned || selectedShip.IsEntered || selectedShip.Equals(ship))
                        continue;
                    if (!(selectedShip is BattleShip)) continue;
                    playSound = true;
                    var enteringShip = (BattleShip)selectedShip;
                    enteringShip.Move(PathFinder.CalculatePath(selectedShip.Position,
                        ship.Position,
                        false));
                    enteringShip.Enter(ship);

                    if (ship.Moving)
                    {
                        enteringShip.Chasing = true;
                    }
                    if (!mEnteringShipList.Contains(enteringShip))
                    {
                        mEnteringShipList.Add(enteringShip);
                    }
                }
                break; //only one ship can be entered at a time
            }
            if (playSound)
            {
                SoundManager.PlayAmb("cmd_board", false);
            }
        }

        /// <summary>
        /// Sets current selected ships in moving state
        /// </summary>
        public void SetShipsMoving()
        {
            int amount = 0;

            //check which ship is closest to the destination
            var closestShip = mSelectShipList[0];
            var distance = Vector2.Distance(closestShip.Position, mMouseInWorldPosition);
            foreach (var ship in mSelectShipList)
            {
                if (Vector2.Distance(ship.Position, mMouseInWorldPosition) < distance)
                {
                    closestShip = ship;
                    distance = Vector2.Distance(closestShip.Position, mMouseInWorldPosition);
                }
            }

            // Set the Move command for every Selected Ship and calculates the Path
            foreach (var ship in mSelectShipList)
            {
                //only if the ship is owned and selected.
                if (!ship.Owned) continue;
                Vector2 destinationAddition = new Vector2(0, 0);
                //the closest ship gets the unmodified path
                if (!ship.Equals(closestShip))
                {
                    destinationAddition = Vector2.Normalize(closestShip.Position - ship.Position) * 100;
                }

                ship.Move(PathFinder.CalculatePath(ship.Position,
                    mMouseInWorldPosition - destinationAddition,
                    false));

                var ship1 = ship as BattleShip;
                if (ship1 != null)
                {
                    var battleShip = ship1;
                    battleShip.CurrentBState = BattleShip.ShipBattleState.Idle;

                }
                else if (ship is TradingShip)
                {
                    var tradingShip = (TradingShip)ship;
                    tradingShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                }
                amount++;
            }
            if (amount > 0)
            {
                SoundManager.PlayAmb(amount > 1 ? "cmd_move_fleet" : "cmd_move", false);
            }
        }
        #endregion

        #region update ships lists
        /// <summary>
        /// Update defending ships
        /// Check for enemy Ships to shoot at while defending(Only defending Ships)
        /// </summary>
        /// <param name="gameTime"></param>
        private void UpdateDefendingShips(GameTime gameTime)
        {
            for (int i = 0; i < mDefendingShipList.Count; i++)
            {
                mDefendingShipList[i].Update(gameTime);
                //check if there are enemy ships in range
                if (mDefendingShipList[i].TargetShip == null)
                {

                    List<AShip> possibleCollisions = new List<AShip>();
                    mShipsQuadTree.Retrieve(possibleCollisions, (AShip)mDefendingShipList[i]);
                    foreach (var ship in possibleCollisions)
                    {
                        var deShip = (AShip)mDefendingShipList[i];
                        CircleF rangeCircle = new CircleF(deShip.Position, 150f);
                        if (rangeCircle.Contains(ship.Position) && !(ship.Owned && deShip.Owned) && !(!ship.Owned && !deShip.Owned))
                        {
                            mDefendingShipList[i].TargetShip = ship;
                            deShip.Moving = false;

                            break;//first ship to be seen will be attacked
                        }
                    }
                }
                //remove not defending ships from list
                var battleShip = mDefendingShipList[i] as BattleShip;
                if (battleShip != null)
                {
                    var defShip = battleShip;
                    if (defShip.CurrentBState != BattleShip.ShipBattleState.Defending)
                    {
                        mDefendingShipList.RemoveAt(i);
                    }
                }
                else if (mDefendingShipList[i] is TradingShip)
                {
                    var defShip = (TradingShip)mDefendingShipList[i];
                    if (defShip.CurrentBState != TradingShip.ShipBattleState.Defending)
                    {
                        mDefendingShipList.RemoveAt(i);
                    }
                }
            }
        }

        /// <summary>
        /// Update for Attacking ships
        /// </summary>
        /// <param name="gameTime"></param>
        private void UpdateAttackingShips(GameTime gameTime)
        {
            for (var i = 0; i < mAttackingShipList.Count; i++)
            {
                mAttackingShipList[i].Update(gameTime);

                if (mAttackingShipList[i].Chasing && mAttackingRefreshRate <= 0 && mAttackingShipList[i].TargetShip != null)
                {
                    
                    
                    var atkShip = (AShip)mAttackingShipList[i];
                    mAttackingRefreshRate = Vector2.Distance(mAttackingShipList[i].TargetShip.Position, atkShip.Position) <= 150 ? 1 : 1;


                    var frontVector = Vector2.Normalize(atkShip.Position - mAttackingShipList[i].TargetShip.Position);
                    Vector2 finalDestination;
                    if (mAttackingShipList.IndexOf(mAttackingShipList[i]) % 2 == 0)
                    {
                        finalDestination = mAttackingShipList[i].TargetShip.Position + (frontVector * 50 + frontVector.PerpendicularClockwise() * 20 * mAttackingShipList.IndexOf(mAttackingShipList[i]));
                    }
                    else
                    {
                        finalDestination = mAttackingShipList[i].TargetShip.Position + (frontVector * 50 + frontVector.PerpendicularCounterClockwise() * 20 * mAttackingShipList.IndexOf(mAttackingShipList[i]));
                    }

                    if (Vector2.Distance(finalDestination, mAttackingShipList[i].TargetShip.Position) >= 150f)
                    {
                        finalDestination = Vector2.Normalize(finalDestination - mAttackingShipList[i].TargetShip.Position) * 70;
                    }
                    atkShip.Move(PathFinder.CalculatePath(atkShip.Position, finalDestination, false));

                    //atkShip.Move(PathFinder.CalculatePath(atkShip.Position, mAttackingShipList[i].TargetShip.Position, false));

                }
                else
                {
                    mAttackingRefreshRate -= gameTime.ElapsedGameTime.TotalSeconds;
                }

                //remove not attacking ships
                var ship = mAttackingShipList[i] as BattleShip;
                if (ship != null)
                {
                    var atkShip = ship;
                    if (atkShip.CurrentBState != BattleShip.ShipBattleState.Attacking)
                    {
                        mAttackingShipList.RemoveAt(i);
                    }
                }
                else if (mAttackingShipList[i] is TradingShip)
                {
                    var atkShip = (TradingShip)mAttackingShipList[i];
                    if (atkShip.CurrentBState != TradingShip.ShipBattleState.Attacking)
                    {
                        mAttackingShipList.RemoveAt(i);
                    }
                }
            }
        }

        /// <summary>
        /// update for all ships repairing
        /// </summary>
        /// <param name="gameTime"></param>
        private void UpdateReparingShips(GameTime gameTime)
        {
            for (var i = 0; i < mRepairingShipList.Count; i++)
            {
                if (mRepairingShipList[i].Hp < mRepairingShipList[i].MaxHp
                   && RessourceManager.GetRessourceFloat("wood") >= mRepairingShipList[i].RepairingValue * 0.01f)
                {

                    mRepairingShipList[i].Hp += mRepairingShipList[i].RepairingValue * 0.005f;
                    //Wood -= mRepairingShipList[i].RepairValue*0.01f;
                    RessourceManager.AddRessourceFloat("wood", -mRepairingShipList[i].RepairingValue * 0.01f);
                }
                else
                {
                    //that no ship can get to much hP with repairing.
                    if (mRepairingShipList[i].Hp > mRepairingShipList[i].MaxHp)
                    {
                        mRepairingShipList[i].Hp = (int)mRepairingShipList[i].MaxHp;
                    }
                    mRepairingShipList[i].Repairing = false;
                    mRepairingShipList.RemoveAt(i);
                }
            }
        }

        /// <summary>
        /// Update for all Shipüs in entering ship list.
        /// </summary>
        /// <param name="gameTime"></param>
        private void UpdateEnteringShips(GameTime gameTime)
        {
            for (int i = 0; i < mEnteringShipList.Count; i++)
            {
                mEnteringShipList[i].Update(gameTime);
                //remove not entering ships from list
                if (mEnteringShipList[i].CurrentBState != BattleShip.ShipBattleState.Entering)
                {
                    mEnteringShipList.RemoveAt(i);
                }
                else
                {
                    //Restriction to Pathrefreshing for Chases
                    if (mEnteringRefreshRate <= 0)
                    {
                        //check if the targetShips are moving and sets new Paths
                        //aktuell immer, weil targetShip nichtmehr verfolgt wird nachdem es stehen bleibt.   
                        if (!mEnteringShipList[i].Chasing) continue;
                        mEnteringShipList[i].Move(PathFinder.CalculatePath(mEnteringShipList[i].Position,
                            mEnteringShipList[i].TargetShip.Position, false));
                        var distance = Vector2.Distance(mEnteringShipList[i].TargetShip.Position,
                            mEnteringShipList[i].Position);
                        if (distance <= 150f)
                        {
                            mEnteringRefreshRate = 1;
                        }
                        else if (distance <= 100f)
                        {
                            mEnteringRefreshRate = 0.5;
                        }
                        else mEnteringRefreshRate = 2;
                    }
                    else
                    {
                        mEnteringRefreshRate -= gameTime.ElapsedGameTime.TotalSeconds;
                    }
                }
            }
            if (EnteringShipList.Count == 0)
            {
                SoundManager.StopAmb("board");//stop sounds 
            }
        }
        #endregion

        #region Input
        /// <summary>
        /// Handle all Input
        /// </summary>
        internal void HandleInput()
        {
            //MouseState mouseState = Mouse.GetState();
            // Calculate the mousePosition in the map
            //mMouseInWorldPosition = mCamera2D.ScreenToWorld(new Vector2(mouseState.X, mouseState.Y));
            mMouseInWorldPosition = Game1.mMapScreen.GetWorldPosition(InputManager.MousePosition().ToVector2());
            var range = ResolutionManager.Scale().X*20;
            
            // Some stuff only used for demonstration.
            // Spawn a battle Ship to the right of the flagship.
            if (InputManager.KeyDown(Keys.I))
            {
                mAiShipManager.SpawnAiBattleShip(FlagShip.Position + 200 * Vector2.UnitX);
            }
            // Spawn the Admiral fleet.
            if (InputManager.KeyDown(Keys.K))
            {
                Game1.mEventScreen.mEventManager.StartQuest3();
            }
            // Spawn the GhostShip.
            if (InputManager.KeyDown(Keys.N))
            {
                Game1.mMapScreen.mPlayerShipManager.mAiShipManager.SpawnGhostShip(new Vector2(4200, 860));
                Game1.mEventScreen.mEventManager.mGhostShipinGame = true;
            }
            // Add KartenFragment
            if (InputManager.KeyDown(Keys.L))
            {
                RessourceManager.AddRessource("mapParts", +1);
            }
            // Spawn own Battleship near us.
            if (InputManager.KeyDown(Keys.J))
            {
                SpawnBattleShip(FlagShip.Position - 200 * Vector2.UnitX, true);
            }

            if (InputManager.LeftMouseButtonDown())
            {
                //check if there are ships selected to sort out how the input should be processed.
                if (mSelectShipList.Count == 0)
                {
                    //check for every Ship, if it is selected
                    foreach (var ship in mAllShipList)
                    {
                        //testweise ein quadrat über die mitte des schiffs.
                        var selectRange = new CircleF(ship.Position, range);
                        if (!selectRange.Contains(mMouseInWorldPosition)) continue;
                        if (VisibilityManager.IsVisible(mMouseInWorldPosition))
                        {
                            ship.Selected = true;
                            mSelectShipList.Add(ship);
                        }

                        break; //when the mouse was clicked, obviously one ship can be selected.
                    }
                }
                else//unselect Ships
                {
                    UnselectShips();
                }
            }
            else if (InputManager.RightMouseButtonDown() && mSelectShipList.Count > 0)
            {                
                if (InputManager.KeyPressed(InputManager.HotKey("Hk1")) || mShipState == ShipState.Attacking)
                {
                    SetShipsAttacking();
                }
                else if (InputManager.KeyPressed(InputManager.HotKey("Hk3")) || mShipState == ShipState.Defending)
                {
                    SetShipsDefending();
                }
                else if (InputManager.KeyPressed(InputManager.HotKey("Hk2")) || mShipState == ShipState.Boarding)
                {
                    SetShipsBoarding();
                }
                else
                {
                    SetShipsMoving();
                }                
            }


            //Selectbox selecting
            if (InputManager.mSelectionBoxFinished)
            {
                InputManager.mSelectionBoxFinished = false;
                var selBoxOld = InputManager.SelectBox();
                var shipsOwned = false;
                foreach (var ship in mAllShipList)
                {
                    if (!selBoxOld.Contains(ship.Position)) continue;
                    if (VisibilityManager.IsVisible(selBoxOld))
                    {
                        ship.Selected = true;
                        mSelectShipList.Add(ship);
                        if (ship.Owned)
                        {
                            shipsOwned = true;
                        }
                    }
                   
                }
                if (shipsOwned)
                {
                    var actuallySelected = new List<AShip>();
                    foreach (var ship in SelectShipList)
                    {
                        if (ship.Owned)
                        {
                            actuallySelected.Add(ship);    
                        }
                        else
                        {
                            ship.Selected = false;
                        }    
                    }
                    SelectShipList = actuallySelected;
                }
            }

            //check for repairing commands
            if (InputManager.KeyPressed(InputManager.HotKey("Hk4")))
            {
                AddRepairingShips();
            }
            else if (InputManager.KeyReleased(InputManager.HotKey("Hk5"))) // Rum
            {
                foreach (var ship in mSelectShipList)
                {
                    if (RessourceManager.GetRessourceInt("rum") > 0)
                    {
                        Random random = new Random();
                        SoundManager.PlayEfx("efx/burping/" + random.Next(1, 7));
                        //increase crew if its the first rum
                        if (ship.RumBuffDuration <= 0f)
                        {
                            ship.AttackValue += 5;
                            ship.EnterAttackValue += 5;
                            ship.RepairingValue += 5;
                            ship.MovementSpeed += 0.1f;
                        }
                        //increase duration and rumCounter
                        ship.RumDrunken++;
                        ship.RumBuffDuration += 5;
                        //ship.RumBuffDuration += 7;
                        RessourceManager.AddRessource("rum", -1);
                    }
                    else
                    {
                        SoundManager.PlayAmb("No_Rum", false);
                    }
                }
            }
            

            //Hud aufrufen            
           /* if (mSelectShipList.Count >= 1)
            {
                HudScreen.HudScreenInstance.ShowShipControl(mSelectShipList);
            }
            else
            {
                HudScreen.HudScreenInstance.HideShipControl();
            }*/
        }

        #endregion

        #region Draw

        /// <summary>
        ///  Renders every Ship.
        /// </summary>
        internal void Draw(SpriteBatch spriteBatch)
        {
            foreach (var s in mAllShipList)
            {
                var shipRect = new Rectangle(
                    (int) (s.Position.X - s.mShipTexture.Width / 2f),
                    (int) (s.Position.Y - s.mShipTexture.Height / 2f),
                    s.mShipTexture.Width,
                    s.mShipTexture.Height);
#if DEBUG
                spriteBatch.DrawRectangle(shipRect, Color.Red, 2f); // Draw a Rectangle around the ship.
#endif
                if (!VisibilityManager.IsVisible(shipRect)) continue; // Skip not visible ships
                
                // rotationstest; auswahl rechteck muss ersetzt werden, da es nicht rotiert werden kann!!elf
                var origin = new Vector2(s.mShipTexture.Width / 2f, s.mShipTexture.Height / 2f);
                spriteBatch.Draw(s.mShipTexture, new Rectangle((int)s.Position.X, (int)s.Position.Y, s.mShipTexture.Width, s.mShipTexture.Height), null, Color.White, s.Direction.ToAngle()-(MathHelper.Pi/2), origin, SpriteEffects.None, 0f);
                
                if (s.Selected)
                {
                    // livebar and selection circle.
                    // Draw Circle when selected. 
                    var scaleRectangle = new Rectangle((int)s.Position.X - s.mShipTexture.Width/2 -10,(int) s.Position.Y - s.mShipTexture.Width/2 -10 , s.mShipTexture.Width + 20, s.mShipTexture.Width + 20);

                    spriteBatch.Draw(mSelectionCircle, scaleRectangle, s.Owned ? Color.Green : Color.Red);
                    if (s.HealthBar == null)
                    {
                        s.HealthBar = new Bar(!s.Owned, s.Hp, s.MaxHp, LanguageManager.GetText("PSM_hp"), mSmolFont, (s.Position + new Vector2(40, -40)), new Rectangle(180, 577, 70, 16), true);
                        s.HealthBar.HealthOrCrewBar = true;
                    }
                    else
                    {
                        s.HealthBar.Update(s.Hp, (s.Position + new Vector2(40, -40)));
                    }                    
                    s.HealthBar.Draw(spriteBatch);
                    
                    if (s.Owned && s.Moving && s.ShipPath.Length > 0)
                    {
                        // draw the destination of the Path.
                        CircleF destCircleF = new CircleF(s.ShipPath.TargetNode.Cell.Center, 15f);
                        spriteBatch.DrawCircle(destCircleF, 4, Color.Black, 5f);
                    }
                }
                
                if (s.IsEntered)
                {
                    if (s.CrewBar == null)
                    {
                        s.CrewBar = new Bar(!s.Owned, s.EnterAttackValue, s.MaxFreePirates, LanguageManager.GetText("PSM_crew"), mSmolFont, (s.Position + new Vector2(40, -60)), new Rectangle(180, 577, 70, 16), true);
                        s.CrewBar.HealthOrCrewBar = true;
                    }
                    else
                    {
                        s.CrewBar.Update(s.EnterAttackValue);
                    }
                    s.CrewBar.Draw(spriteBatch);
                }

                var ship = s as BattleShip;
                var bShip = ship;
                if (bShip?.CurrentBState == BattleShip.ShipBattleState.Entering && bShip.Docking)
                {
                    if (ship.CrewBar == null)
                    {
                        ship.CrewBar = new Bar(!bShip.Owned, ship.EnterAttackValue, ship.MaxFreePirates, LanguageManager.GetText("PSM_crew"), mSmolFont, (ship.Position + new Vector2(40, -60)), new Rectangle(180, 577, 70, 16), true);
                        ship.CrewBar.HealthOrCrewBar = true;
                    }
                    else
                    {
                        ship.CrewBar.Update(ship.EnterAttackValue, ship.Position);
                    }
                    ship.CrewBar.Draw(spriteBatch);
                }

                if (DebugDrawPath)
                {
                    DebugPathDraw(spriteBatch, s.ShipPath);
                }
            }
        }

        #endregion

        #region Helper

        /// <summary>
        ///  Spawns a certain Number of Ships at the start of the game
        /// </summary>
        private void SpawnShips()
        {
            //initialize Flagship manually
            FlagShip = new FlagShip(new Vector2(100, 120)) {Hp = 60};
            mAllShipList.Add(FlagShip);
            mPlayerShipsList.Add(FlagShip);

#if DEBUG
            // For Savegame manipulation.
            SpawnBattleShip(new Vector2(100, 100), true);
            SpawnBattleShip(new Vector2(100, 140), true);
            // SpawnBattleShip(new Vector2(4600, 870), true);
            // SpawnBattleShip(new Vector2(4600, 890), true);
            RessourceManager.AddRessource("rum", +32);
            RessourceManager.AddRessource("wood", +342);
            RessourceManager.AddRessource("gold", +438);
           // RessourceManager.AddRessource("mapParts", +4);
#endif
        }

        /// <summary>
        /// Getter for the AllShipList
        /// </summary>
        /// <returns></returns>
        public IEnumerable<AShip> GetAllShips()
        {
            return mAllShipList;
        }

        /// <summary>
        ///  creates a new BattleShip with the specified position and owner.
        /// <param name="position"> The Spawnposition of the ship</param>
        /// <param name="owned"> The owner of the Ship. True if the player owns the ship</param>
        /// </summary>
        // ReSharper disable once UnusedMethodReturnValue.Global
        public void SpawnBattleShip(Vector2 position, bool owned)
        {
            var bShip = new BattleShip(position)
            {
                Owned = owned,
                mShipTexture =
                    Game1.mContentManager.Load<Texture2D>(owned
                        ? "Ships/battle_ship_texture"
                        : "Ships/enemy_ship_texture")
            };
            mAllShipList.Add(bShip);
            if (owned)
            {
                mPlayerShipsList.Add(bShip);
            }
        }

        /// <summary>
        ///  creates a new TradingShip with the specified position and owner.
        /// <param name="position"> The Spawnposition of the ship</param>
        /// <param name="owned"> The owner of the Ship. True if the player owns the ship</param>
        /// </summary>
        // ReSharper disable once UnusedMethodReturnValue.Global
        public void SpawnTradingShip(Vector2 position, bool owned)
        {
            var tShip = new TradingShip(position) { Owned = owned };
            mAllShipList.Add(tShip);
            if (owned)
            {
                mPlayerShipsList.Add(tShip);
            }
        }


        /// <summary>
        ///  sets selected value of every currently Selected ship to false and clears the selectedShipList.
        /// </summary>
        private void UnselectShips()
        {
            foreach (var ship in mSelectShipList)
            {
                ship.Selected = false;
            }
            mSelectShipList.Clear();
        }


        /// <summary>
        /// Returns the currently selected ship.s
        /// </summary>
        /// <returns>List of AShip objects</returns>
        public List<AShip> GetSelectedShips()
        {
            return mSelectShipList;
        }

        /// <summary>
        /// Returns the ammount of selected ships.
        /// </summary>
        /// <returns></returns>
        public int GetSelectedShipsLength()
        {
            return mSelectShipList.Count;
        }

        #endregion

        #region Debug
        
        /// <summary>
        /// Draws a Path
        /// </summary>
        /// <param name="spriteBatch"></param>
        /// <param name="path"></param>
        private void DebugPathDraw(SpriteBatch spriteBatch, Path path)
        {
            if (path == null) return;
            var pathCopy = path.Copy();
            while (!pathCopy.Finished)
            {
                //Draw the cells
                spriteBatch.Draw(mDummyTexture, new Rectangle(pathCopy.Next.Cell.Position.ToPoint(), new Point(16, 16)), Color.BlueViolet);
                pathCopy.GetNextWaypoint();
            }
        }

        #endregion
    }
}
