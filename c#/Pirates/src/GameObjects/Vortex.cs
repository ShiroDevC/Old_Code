using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using MonoGame.Extended.Animations.SpriteSheets;
using pirates.GameObjects.SmallThings;
using pirates.Managers;
using pirates.Screens;

namespace pirates.GameObjects
{
    class Vortex
    {
        private Rectangle mVortexRegion1;
        private Rectangle mVortexRegion2;
        private SpriteSheetAnimationFactory mAnim;
        private int mVortexCounter, mTimeToLive;
        private bool mCoolDown;
        private int mCoolDownCounter;
        private VortexAnim mVortexAnim;
        private VortexAnim mVortexAnim2;
        internal bool mDestroyed;


        /// <summary>
        /// Creates a new teleportation vortex
        /// </summary>
        /// <param name="vortexanim">vortexanimation</param>
        public Vortex(SpriteSheetAnimationFactory vortexanim)
        {
            var generator = new Random();
            mAnim = vortexanim;

            mVortexRegion1 = new Rectangle(generator.Next(0, Game1.mMapScreen.mMapCamera.mMapHeight),
                generator.Next(0, Game1.mMapScreen.mMapCamera.mMapWidth/4), 175 , 100);

            mVortexRegion2 = new Rectangle(generator.Next(0, Game1.mMapScreen.mMapCamera.mMapHeight),
                generator.Next(0, Game1.mMapScreen.mMapCamera.mMapWidth/4), 175, 100);

            // check whether the selected coordinates are on water
            while (true)
            {
                var location1 = Game1.mMapScreen.mGridMap.PosToGrid(mVortexRegion1.Location.ToVector2());
                var location2 = Game1.mMapScreen.mGridMap.PosToGrid(mVortexRegion2.Location.ToVector2());
                if (Game1.mMapScreen.mGridMap.GridCells[(int)location1.X, (int)location1.Y].IsWalkable &&
                    (Game1.mMapScreen.mGridMap.GridCells[(int)location2.X, (int)location2.Y].IsWalkable))
                {
                    break;
                }

                mVortexRegion1 = new Rectangle(generator.Next(0, Game1.mMapScreen.mMapCamera.mMapHeight),
                    generator.Next(0, Game1.mMapScreen.mMapCamera.mMapWidth),
                    175,
                    100);

                mVortexRegion2 = new Rectangle(generator.Next(0, Game1.mMapScreen.mMapCamera.mMapHeight),
                    generator.Next(0, Game1.mMapScreen.mMapCamera.mMapWidth),
                    175,
                    100);

            }

            // setting up the animations
            mVortexAnim = new VortexAnim(mAnim, mVortexRegion1.Location.ToVector2() + new Vector2(60, 20));
            MapScreen.mSmallThingsManager.AddThing(mVortexAnim);

            mVortexAnim2 = new VortexAnim(mAnim, mVortexRegion2.Location.ToVector2() + new Vector2(60, 20));
            MapScreen.mSmallThingsManager.AddThing(mVortexAnim2);

            mTimeToLive = generator.Next(3000, 10000);
        }

        public void Update(QuadTree quadTree)
        {
            // repeat the vortexanimation
            if (mVortexAnim.IsDestroyed && !mDestroyed)
            {
                mVortexAnim = new VortexAnim(mAnim, mVortexRegion1.Location.ToVector2());
                mVortexAnim2 = new VortexAnim(mAnim, mVortexRegion2.Location.ToVector2());
                MapScreen.mSmallThingsManager.AddThing(mVortexAnim);
                MapScreen.mSmallThingsManager.AddThing(mVortexAnim2);
            }


            // damage a ship if its too close to a storm.
            FisherShip dummyShip1 = new FisherShip(new Vector2(mVortexRegion1.X, mVortexRegion1.Y));
            var possibleCollisions1 = new List<AShip>();
            quadTree.Retrieve(possibleCollisions1, dummyShip1);

            FisherShip dummyShip2 = new FisherShip(new Vector2(mVortexRegion1.X, mVortexRegion1.Y));
            var possibleCollisions2 = new List<AShip>();
            quadTree.Retrieve(possibleCollisions2, dummyShip2);

            if (possibleCollisions1.Count > 0 || possibleCollisions2.Count > 0)
            {
                foreach (var pCShip in possibleCollisions1)
                {
                    if (mVortexRegion1.Contains(pCShip.Position) &&
                        pCShip.Owned && !mCoolDown)
                    {
                        SoundManager.PlayEfx("efx/warp");
                        pCShip.Position = mVortexRegion2.Location.ToVector2();
                        pCShip.Moving = false;
                        /*
                        if (pCShip is FlagShip)
                        {
                            Game1.mMapScreen.mMapCamera.Position = (mVortexRegion2.Location.ToVector2() - new Vector2(60, 20));
                        }
                        */
                        mCoolDown = true;
                    }
                    if (mVortexRegion2.Contains(pCShip.Position) &&
                        pCShip.Owned && !mCoolDown)
                    {
                        SoundManager.PlayEfx("efx/warp");
                        pCShip.Position = mVortexRegion1.Location.ToVector2();
                        pCShip.Moving = false;

                        /*
                        if (pCShip is FlagShip)
                        {
                            Game1.mMapScreen.mMapCamera.Position = (mVortexRegion1.Location.ToVector2() -
                                                                   new Vector2(60, 20));
                        }
                        */
                        mCoolDown = true;
                    }
                }
            }

            // cooldown for disallowing multiple teleportations
            if (mCoolDown)
            {
                if (mCoolDownCounter < 300)
                {
                    mCoolDownCounter += 1;
                }
                else
                {
                    mCoolDownCounter = 0;
                    mCoolDown = false;
                }
            }

            mTimeToLive -= 1;

            if (mTimeToLive < 0)
            {
                mDestroyed = true;
                EnvironmentManager.mVortexNumber -= 1;
                mVortexAnim.KillVortex();
                mVortexAnim2.KillVortex();
            }

        }
    }
}
