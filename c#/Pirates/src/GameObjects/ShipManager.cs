using System.Collections.Generic;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using MonoGame.Extended;
using MonoGame.Extended.Shapes;
using pirates.AI.Pathfinding;
using pirates.GameObjects.SmallThings;
using pirates.GUI;
using pirates.Managers;
using pirates.Map;
using pirates.Screens;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Manages the Selection, Movement and Battle of the Ships. 
    ///  Processes Input for the given commands and Draws all Ships. 
    /// </summary>
    public sealed class ShipManager
    {
        /// <summary>
        ///  The List of all Ships in the game.
        /// </summary>
        private static List<AShip> sAllShipList = new List<AShip>();

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> AllShips
        {
            get { return sAllShipList; }
            set { sAllShipList = value; }
        }

        /// <summary>
        ///  List of all selected ships.
        /// </summary>
        private static List<AShip> sSelectShipList;

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> SelectShipList
        {
            get { return sSelectShipList; }
            set { sSelectShipList = value; }
        }

        /// <summary>
        ///  List of all currently repairing Ships.
        /// </summary>
        private List<AShip> mRepairingShipList;

        // ReSharper disable once MemberCanBePrivate.Global (needed for XmlSerializer).
        public List<AShip> RepairingShipList
        {
            get { return mRepairingShipList; }
            set { mRepairingShipList = value; }
        }

        /// <summary>
        ///  List of all currently fighting(Attacking) Ships.
        /// </summary>
        private List<IBattleObject> mAttackingShipList;

        public List<IBattleObject> AttackingShipList
        {
            get { return mAttackingShipList; }
            set { mAttackingShipList = value; }
        }

        /// <summary>
        ///  List of all Ships in Defense Mode.
        /// </summary>
        private List<IBattleObject> mDefendingShipList;

        public List<IBattleObject> DefendingShipList
        {
            get { return mDefendingShipList; }
            set { mDefendingShipList = value; }
        }

        /// <summary>
        ///  List of all Ships in Defense Mode.
        /// </summary>
        private List<BattleShip> mEnteringShipList;

        public List<BattleShip> EnteringShipList
        {
            get { return mEnteringShipList; }
            set { mEnteringShipList = value; }
        }

        private readonly IBulletFactory mBulletFactory;

        internal QuadTree mShipsQuadTree;

        /// <summary>
        ///  The ContentManager for loading Textures.
        /// </summary>
        private readonly ContentManager mContentManager;

/*
        /// <summary>
        ///  Texture for WarShips.
        /// </summary>
        private Texture2D mWarShipSprite;


        /// <summary>
        ///  Texture for FisherShips.
        /// </summary>
        private Texture2D mFisherShipSprite;

        /// <summary>
        ///  Texture for TradingShips.
        /// </summary>
        private Texture2D mTradingShipSprite;
*/
        /// <summary>
        ///  Texture for the FlagShip.
        /// </summary>
        private Texture2D mFlagShipSprite;

        /// <summary>
        ///  Texture for the Selectioncircle
        /// </summary>
        private Texture2D mSelectionCircle;

        /// <summary>
        ///  The positon of the Mouse. Is used for selecting and commands.
        /// </summary>
        private Vector2 mMouseInWorldPosition;

        /// <summary>
        ///  PathFinder for the Movement of the Ship.
        /// </summary>
        private readonly PathFinder mPathFinder;

        /// <summary>
        /// Dummy Texture used for debugging
        /// </summary>
        private Texture2D mDummyTexture;

        /// <summary>
        /// Will draw the paths for ships if set to true.
        /// </summary>
        // ReSharper disable once MemberCanBePrivate.Global
        // ReSharper disable once UnusedAutoPropertyAccessor.Local
        public bool DebugDrawPath { get; private set; }

        /// <summary>
        /// The rate in seconds, in which the Path for Chasing is refreshed when entering.
        /// </summary>
        private double mEnteringRefreshRate;

        /// <summary>
        /// The rate in seconds, in which the Path for Chasing is refreshed when attacking.
        /// </summary>
        private double mAttackingRefreshRate;

        /// <summary>
        /// the font for the HP-Bars
        /// </summary>
        private SpriteFont mSmolFont;

        public ShipManager()
        {
            mPathFinder = new PathFinder(Game1.mMapScreen.mGridMap);
            mContentManager = Game1.mScreenManager.Game.Content;
        }

        /// <summary>
        ///  Constructor for the ShipManager.
        /// /// <param name="gridMap"> The GridMap for the PathFinder</param>
        /// </summary>
        public ShipManager(IGridMap gridMap, ContentManager content, IBulletFactory bulletFactory)
        {
            mPathFinder = new PathFinder(gridMap);
            mContentManager = content;
            mBulletFactory = bulletFactory;
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

        /// <summary>
        /// Unloads all Textures of the Ships.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        public void UnloadContent()
        {
            mContentManager.Unload();
        }

        /// <summary>
        ///  Spawns a certain Number of Ships
        /// </summary>
        public void SpawnShips()
        {
            sSelectShipList = new List<AShip>();
            sAllShipList = new List<AShip>();
            mAttackingShipList = new List<IBattleObject>();
            mDefendingShipList = new List<IBattleObject>();
            mRepairingShipList = new List<AShip>();
            mEnteringShipList = new List<BattleShip>();
            
            //instanziation
            FlagShip testShip = new FlagShip(new Vector2(20,20));
            BattleShip testBattleShip = new BattleShip(new Vector2(300,100));
            BattleShip testBattleShip2 = new BattleShip(new Vector2(550, 900));
            FisherShip testFisherShip = new FisherShip(new Vector2(550, 700));
            TradingShip testTradingShip = new TradingShip(new Vector2(100, 1000));

            //initialization
            testBattleShip.Initialize();
            testBattleShip2.Initialize();
            testShip.Initialize();
            testFisherShip.Initialize();
            testTradingShip.Initialize();

            //Owned
            testBattleShip.Owned = true;
            
            //add to List
            sAllShipList.Add(testShip);
            sAllShipList.Add(testBattleShip);
            sAllShipList.Add(testBattleShip2);
            sAllShipList.Add(testFisherShip);
            sAllShipList.Add(testTradingShip);
            
            //testing behaviour
            //testBattleShip2.Defend(mPathFinder.CalculatePath(testBattleShip2.Position, new Vector2(100, 150), true));
            testTradingShip.Defend(mPathFinder.CalculatePath(testTradingShip.Position, new Vector2(100, 100), true));//4700, 1400
            mDefendingShipList.Add(testTradingShip);
            //mDefendingShipList.Add(testBattleShip2);


            //testing repairing
            testBattleShip.Hp = 80;

            //testing QuadTree:
            mShipsQuadTree = new QuadTree(0, new Rectangle(0,0,5760,5760));//testmap size is 1000*1000
            
        }

        /// <summary>
        ///  Respawns Ships according to the current count of Ships.
        ///  Also adjusts the Attributes of the Ships to make the game fair. 
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        public void RespawnShips()
        {
            //todo: Implement Respawn pattern for Ships
        }

        public static List<AShip> GetAllShips()
        {
            return sAllShipList;
        }

        /// <summary>
        ///  Calls update() on every ship. Checks for input and manages Selecting 
        /// and the execution of commands.
        /// </summary>
        public void Update(GameTime gameTime)
        {
            mShipsQuadTree.Clear();
            foreach (var shipu in AllShips)
            {
                mShipsQuadTree.Insert(shipu);
            }
            //general update for all ships
            for (int i = 0; i < sAllShipList.Count; i++)
            {
                sAllShipList[i].UpdateMoving(gameTime);
                if (sAllShipList[i].Hp <= 0)
                {
                    sAllShipList.RemoveAt(i);
                }
            }
            //Call Update for every Attacking Ship
            for (int i = 0; i < mAttackingShipList.Count; i++)
            {
                mAttackingShipList[i].Update(gameTime);

                if (mAttackingShipList[i].Chasing && mAttackingRefreshRate <= 0)
                {
                    mAttackingRefreshRate = 2;
                    var atkShip = (AShip) mAttackingShipList[i];
                    atkShip.Move(mPathFinder.CalculatePath(atkShip.Position, mAttackingShipList[i].TargetShip.Position, true));
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

            //Check for enemy Ships to shoot at while defending(Only defending Ships)
            for (int i = 0; i < mDefendingShipList.Count; i++)
            {
                mDefendingShipList[i].Update(gameTime);
                //check if there are enemy ships in range
                if (mDefendingShipList[i].TargetShip == null)
                {
                    /* old version, as backup...
                    foreach (var ship in sAllShipList)
                    {

                        var deShip = (AShip) mDefendingShipList[i];
                        CircleF rangeCircle = new CircleF(deShip.Position, 100f);
                        if (rangeCircle.Contains(ship.Position) && !(ship.Owned && deShip.Owned) && !(!ship.Owned && !deShip.Owned))
                        {
                            mDefendingShipList[i].TargetShip = ship;
                            //deShip.Moving = false;
                            
                            break;//first ship to be seen will be attacked
                        }
                     } */

                    //QuadTree test
                    List<AShip> possibleCollisions = new List<AShip>();
                    mShipsQuadTree.Retrieve(possibleCollisions,(AShip)mDefendingShipList[i]);
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

            //Update and Pathrefreshing for Entering Ships
            for (int i = 0; i < mEnteringShipList.Count; i++)
            {   
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
                        mEnteringRefreshRate = 2;
                        //check if the targetShips are moving and sets new Paths
                        //aktuell immer, weil targetShip nichtmehr verfolgt wird nachdem es stehen bleibt.
                        
                        if (mEnteringShipList[i].Chasing)
                        {
                            mEnteringShipList[i].Move(mPathFinder.CalculatePath(mEnteringShipList[i].Position,
                                mEnteringShipList[i].TargetShip.Position,true));
                        }

                        /*
                        Alternative: zu inteligent wahrscheinlich...
                        if (mEnteringShipList[i].Chasing &&
                            !mEnteringShipList[i].ShipPath.TargetNode.Equals(mEnteringShipList[i].TargetShip.ShipPath.TargetNode))
                        {
                            mEnteringShipList[i].Move(mPathFinder.CalculatePath(mEnteringShipList[i].Position,
                                mEnteringShipList[i].TargetShip.ShipPath.TargetNode.Cell.Position,true));
                        }
                        */
                        
                    }
                    else
                    {
                        mEnteringRefreshRate -= gameTime.ElapsedGameTime.TotalSeconds;
                    }
                   mEnteringShipList[i].Update(gameTime);
                }
                
               


            }

            //todo: check if hudScreen is in selecting process for attack/defense/enter
            //only check input if the specified boolean(from hud) is false 

            

            //update for all ships repairing
            for (var i = 0; i < mRepairingShipList.Count; i++)
            {
                 if (mRepairingShipList[i].Hp < mRepairingShipList[i].MaxHp
                    && RessourceManager.GetRessourceFloat("wood") >= mRepairingShipList[i].RepairValue*0.01f)
                    {

                    mRepairingShipList[i].Hp += mRepairingShipList[i].RepairValue*0.005f;
                        //Wood -= mRepairingShipList[i].RepairValue*0.01f;
                    RessourceManager.AddRessourceFloat("wood", -mRepairingShipList[i].RepairValue * 0.01f);
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

        internal void HandleInput(GameTime gameTime)
        {
            //MouseState mouseState = Mouse.GetState();
            // Calculate the mousePosition in the map
            //mMouseInWorldPosition = mCamera2D.ScreenToWorld(new Vector2(mouseState.X, mouseState.Y));
            mMouseInWorldPosition = Game1.mMapScreen.GetWorldPosition(InputManager.MousePosition().ToVector2());
            float range = ResolutionManager.Scale().X*20;
            if (InputManager.LeftMouseButtonDown())
            {
                //check if there are ships selected to sort out how the input should be processed.
                if (sSelectShipList.Count == 0)
                {
                    //check for every Ship, if it is selected
                    foreach (var ship in sAllShipList)
                    {
                        // todo: How to rotate the selection "Box" of the Ship acording to its direction?
                        //testweise ein quadrat über die mitte des schiffs.
                        CircleF selectRange = new CircleF(ship.Position, range);
                        if (selectRange.Contains(mMouseInWorldPosition))
                        {
                            ship.Selected = true;
                            sSelectShipList.Add(ship);
                            break;//when the mouse was clicked, obviously one ship can be selected.
                        }
                    }
                }
                else
                {
                    //check for attack commands
                    if (InputManager.KeyPressed(Keys.C))
                    {
                        //check if there is a ship at the position that was clicked
                        foreach (var ship in sAllShipList)
                        {
                            //testweise ein quadrat über die mitte des schiffs.
                            Rectangle selectRange = new Rectangle((int)ship.Position.X - 20, (int)ship.Position.Y - 20, 40, 40);//new Rectangle(ship.Position.ToPoint(), new Point(100, 40));
                            if (selectRange.Contains(mMouseInWorldPosition)&& !ship.Owned)
                            {
                                //every selected ship attacks the target ship
                                foreach (var selectedShip in sSelectShipList)
                                {
                                    if (selectedShip.Owned && !selectedShip.IsEntered)
                                    {
                                        selectedShip.Move(mPathFinder.CalculatePath(selectedShip.Position, ship.Position, true));
                                        var attackingShip = (IBattleObject) selectedShip;
                                        attackingShip.Attack(ship);
                                        mAttackingShipList.Add(attackingShip);
                                    }
                                    
                                    
                                }
                                break;//only one ship can be attacked at a time
                            }
                        }
                        UnselectShips();
                    }
                    else if (InputManager.KeyPressed(Keys.F)) //Defending Mode
                    {
                        foreach (var ship in sSelectShipList)
                        {
                            if (ship.Owned && !ship.IsEntered)
                            {
                                var defendingShip = (IBattleObject)ship;
                                defendingShip.Defend(mPathFinder.CalculatePath(ship.Position, mMouseInWorldPosition, true));
                                mDefendingShipList.Add(defendingShip);
                            }
                            
                        }
                        UnselectShips();
                    }else if (InputManager.KeyPressed(Keys.Q))//Entering
                    {
                        foreach (var ship in sAllShipList)
                        {
                            //testweise ein quadrat über die mitte des schiffs.
                            var selectRange = new Rectangle((int)ship.Position.X - 20, (int)ship.Position.Y - 20, 40, 40);
                            if (selectRange.Contains(mMouseInWorldPosition) && !ship.Owned)
                            {
                                //every selected ship attacks the target ship
                                foreach (var selectedShip in sSelectShipList)
                                {
                                    if (selectedShip.Owned && !selectedShip.IsEntered && !selectedShip.Equals(ship))
                                    {
                                        if (selectedShip is BattleShip)
                                        {
                                           var enteringShip = (BattleShip) selectedShip;
                                           enteringShip.Move(mPathFinder.CalculatePath(selectedShip.Position, ship.Position, true));
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
                                        
                                        
                                    }


                                }
                                break;//only one ship can be entered at a time
                            }
                        }
                        UnselectShips();

                    }
                    else
                    {
                        // Set the Move command for every Selected Ship and calculates the Path
                        foreach (var ship in sSelectShipList)
                        {
                            //only if the ship is owned and selected.
                            if (ship.Owned)
                            {
                                ship.Move(mPathFinder.CalculatePath(ship.Position,mMouseInWorldPosition, true));
                                if (ship is BattleShip)
                                {
                                    var battleShip = (BattleShip) ship;
                                    battleShip.CurrentBState = BattleShip.ShipBattleState.Idle;
                                    
                                }else if (ship is TradingShip)
                                {
                                    var tradingShip = (TradingShip) ship;
                                    tradingShip.CurrentBState = TradingShip.ShipBattleState.Idle;
                                }
                               
                            }

                        }
                        
                       UnselectShips();

                    }


                    
                }

            }

            //Selectbox selecting
            if (InputManager.mSelectionBoxFinished)
            {
                // Inputmanager no longer supports "mouseInWorld" -> added these three lines, code still working - Jonas
                InputManager.mSelectionBoxFinished = false;
                var selBoxOld = InputManager.SelectBox();
                var newCoords = Game1.mMapScreen.GetWorldPosition(new Vector2(selBoxOld.X, selBoxOld.Y));
                var selBox = new Rectangle((int)newCoords.X, (int)newCoords.Y, selBoxOld.Width, selBoxOld.Height);
                var shipsOwned = false;
                foreach (var ship in sAllShipList)
                {
                    if (!selBox.Contains(ship.Position)) continue;
                    ship.Selected = true;
                    sSelectShipList.Add(ship);
                    if (ship.Owned)
                    {
                        shipsOwned = true;
                    }
                }
                if (shipsOwned)
                {
                    for (var i = 0; i < sSelectShipList.Count; i++)
                    {
                        if (sSelectShipList[i].Owned == false)
                        {
                            sSelectShipList[i].Selected = false;
                            sSelectShipList.RemoveAt(i);
                            
                        }
                    }
                }
            }

            //check for repairing commands
            if (InputManager.KeyPressed(Keys.R))
            {
                foreach (var ship in sSelectShipList)
                {
                    if (ship.Owned && !mRepairingShipList.Contains(ship))
                    {
                        ship.Repairing = true;
                        mRepairingShipList.Add(ship);
                    }
                    
                }
            }
            


            // deselect all ships.
            if (InputManager.RightMouseButtonDown())
            {
                UnselectShips();
            }


            //Hud aufrufen
            if (sSelectShipList.Count >= 1)
            {
                HudScreen.HudScreenInstance.ShowShipControl(sSelectShipList);
            }
            else
            {
                HudScreen.HudScreenInstance.HideShipControl();
            }
        }
        /*

        // ReSharper disable once UnusedMember.Global
        public void RepairShips(List<AShip> toBeRepaired)
        {
            mRepairingShipList = toBeRepaired;
            foreach (var ship in mRepairingShipList)
            {
                // setting the ship to repair and stops movement.
                ship.Repairing = true;
            }
        }*/

        /// <summary>
        ///  creates a new BattleShip with the specified position and owner.
        /// <param name="position"> The Spawnposition of the ship</param>
        /// <param name="owned"> The owner of the Ship. True if the player owns the ship</param>
        /// </summary>
        public static AShip SpawnBattleShip(Vector2 position, bool owned)
        {
             return new BattleShip(position) {Owned = owned};  
        }

        /// <summary>
        ///  creates a new TradingShip with the specified position and owner.
        /// <param name="position"> The Spawnposition of the ship</param>
        /// <param name="owned"> The owner of the Ship. True if the player owns the ship</param>
        /// </summary>
        public static AShip SpawnTradingShip(Vector2 position, bool owned)
        {
            return new TradingShip(position) {Owned = owned};
        }


        /// <summary>
        ///  sets selected value of every currently Selected ship to false and clears the selectedShipList.
        /// </summary>
        private void UnselectShips()
        {
            foreach (var ship in sSelectShipList)
            {
                ship.Selected = false;
            }
            sSelectShipList.Clear();
        }

        public static int GetSelectedShipsLength()
        {
            return sSelectShipList.Count;
        }

        /// <summary>
        ///  Renders every Ship.
        /// </summary>
        public void Draw(SpriteBatch spriteBatch)
        {
            //todo: Only rendering when in viewport + change documentation acordingly
            //Uses the SpriteBatch from the GameScreen
            foreach (var s in sAllShipList)
            {
                //Draw ohne rotation
                //spriteBatch.Draw(mShipTextures[s.GetType()], s.Position, Color.White);

                // rotationstest; auswahl rechteck muss ersetzt werden, da es nicht rotiert werden kann!! todo:
                Vector2 origin = new Vector2(s.mShipTexture.Width / 2f, s.mShipTexture.Height / 2f);
                spriteBatch.Draw(s.mShipTexture, new Rectangle((int)s.Position.X, (int)s.Position.Y, s.mShipTexture.Width, s.mShipTexture.Height), null, Color.White, s.Direction.ToAngle()-(MathHelper.Pi/2), origin, SpriteEffects.None, 0f);

                //livebar drawing
                //Draw Circle when selected.
                if (s.Selected)
                {
                    //spriteBatch.Draw(mSelectionCircle, new Vector2(s.Position.X - (mSelectionCircle.Width/2), s.Position.Y ), Color.White);
                    var scaleRectangle = new Rectangle((int)s.Position.X - s.mShipTexture.Width/2 -10,(int) s.Position.Y - s.mShipTexture.Width/2 -10 , s.mShipTexture.Width + 20, s.mShipTexture.Width + 20);
                    Bar liveBar;
                    if (s.Owned)
                    {
                       spriteBatch.Draw(mSelectionCircle,scaleRectangle, Color.Green); 
                       liveBar = new Bar(false, s.Hp, s.MaxHp, "HP", mSmolFont, (s.Position + new Vector2(40, -40)), new Rectangle(180, 577, 70, 16), true);
                       
                    }
                    else
                    {
                        spriteBatch.Draw(mSelectionCircle, scaleRectangle, Color.Red);
                        liveBar = new Bar(true, s.Hp, s.MaxHp, "HP", mSmolFont, (s.Position + new Vector2(40, -40)), new Rectangle(180, 577, 70, 16), true);
                    }
                    liveBar.Draw(spriteBatch);
                    if (s.Moving)
                    {
                        //draw the destination of the Path.
                        CircleF destCircleF = new CircleF(s.ShipPath.TargetNode.Cell.Position, 15f);
                        spriteBatch.DrawCircle(destCircleF,4,Color.Black, 5f);
                    }
                    

                }


                if (DebugDrawPath)
                {
                    DebugPathDraw(spriteBatch, s.ShipPath);
                }
            }
        }


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
    }
}
