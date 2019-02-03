using System;
using System.Collections.Generic;
using Microsoft.Xna.Framework;
using MonoGame.Extended.Animations.SpriteSheets;
using pirates.GameObjects.SmallThings;
using pirates.Managers;
using pirates.Screens;

namespace pirates.GameObjects
{
    /// <summary>
    /// A Storm
    /// </summary>
    sealed class Storm
    {
        private Rectangle mStormRegion;
        private SpriteSheetAnimationFactory mAnim;
        private int mCounter, mLightningCounter, mNewLightning, mTimeToLive;
        private readonly Random mGenerator;
        // maximum number of clouds in a storm
        private readonly int mStormCloudLimit = 30;
        private bool mLightningactivated;
        private Cloud mCheckCloud;
        internal bool mDestroyed;
        private List<Cloud> mStormClouds;

        public Storm(SpriteSheetAnimationFactory lightningAnimation)
        {
            mGenerator = new Random();
            mAnim = lightningAnimation;

            mStormClouds = new List<Cloud>();

            mStormRegion = new Rectangle(mGenerator.Next(0, Game1.mMapScreen.mMapCamera.mMapHeight),
                mGenerator.Next(0, Game1.mMapScreen.mMapCamera.mMapWidth), mGenerator.Next(300, 1000), mGenerator.Next(200, 700));

            mNewLightning = mGenerator.Next(10, 100);
            Spawn();
            mLightningactivated = false;
            mTimeToLive = mGenerator.Next(0, 200);
        }


        public void Update(QuadTree quadTree)
        {
            if (mLightningactivated)
            {
                // damage a ship if its too close to a storm.
                FisherShip dummyShip = new FisherShip(new Vector2(mStormRegion.X+ (mStormRegion.Width/2), mStormRegion.Y + (mStormRegion.Height/2)));
                var possibleCollisions = new List<AShip>();
                quadTree.Retrieve(possibleCollisions, dummyShip);
                if (possibleCollisions.Count > 0)
                {
                    foreach (var pCShip in possibleCollisions)
                    {
                        if (mStormRegion.Contains(pCShip.Position) && mCounter >= 500 &&
                            pCShip.Owned)
                        {
                            var lightning = new Lightning(mAnim, pCShip.Position - new Vector2(0, 75));
                            MapScreen.mSmallThingsManager.AddThing(lightning);
                            if (pCShip.Owned)
                            {
                                SoundManager.PlayEfx("efx/ambience/Storm/rain_thunder");
                            }
                            pCShip.Hp -= 1;
                            mCounter = 0;
                        }
                        if (mStormRegion.Contains(pCShip.Position) && mCounter < 500)
                        {
                            mCounter += 1;

                        }
                    }
                }


                if (mLightningCounter >= mNewLightning)
                    {
                        var lightning = new Lightning(mAnim,
                            new Vector2(mGenerator.Next(mStormRegion.X + 75, mStormRegion.X + mStormRegion.Width - 75),
                                mGenerator.Next(mStormRegion.Y + 75, mStormRegion.Y + mStormRegion.Height - 75)));
                        MapScreen.mSmallThingsManager.AddThing(lightning);
                        mLightningCounter = 0;
                        mNewLightning = mGenerator.Next(10, 100);
                        mTimeToLive -= 1;
                        if (mTimeToLive < 0)
                        {
                            SoundManager.Stop("efx/ambience/Storm/rain_thunder");
                            mDestroyed = true;
                            EnvironmentManager.mStormNumber -= 1;
                            Despawn();
                            if (mCheckCloud.mDespawnComplete)
                            {
                                foreach (var cloud in mStormClouds)
                                {
                                    cloud.KillCloud();
                                }

                            }
                        }
                    }
                    else
                    {
                        mLightningCounter += 1;
                    }                   
                   
                
            }
            else
            {
                if (mCheckCloud.mFadingCompleted)
                {
                    mLightningactivated = true;
                }
            }


        }

        private void Spawn()
        {
            mCheckCloud = new Cloud(EnvironmentManager.mStormCloudList[mGenerator.Next(0, EnvironmentManager.mStormCloudList.Count)], 0,
                    new Vector2(mGenerator.Next(mStormRegion.X, mStormRegion.X + mStormRegion.Width),
                    mGenerator.Next(mStormRegion.Y, mStormRegion.Y + mStormRegion.Height)), true);
            MapScreen.mSmallThingsManager.AddThing(mCheckCloud);
            for (int i = 0; i <= mStormCloudLimit; i++)
            {
                var cloud = new Cloud(EnvironmentManager.mStormCloudList[mGenerator.Next(0, EnvironmentManager.mStormCloudList.Count)], 0,
                    new Vector2(mGenerator.Next(mStormRegion.X, mStormRegion.X + mStormRegion.Width),
                    mGenerator.Next(mStormRegion.Y, mStormRegion.Y + mStormRegion.Height)), true);
                MapScreen.mSmallThingsManager.AddThing(cloud);
                mStormClouds.Add(cloud);
            }
        }

        private void Despawn()
        {
            foreach (var cloud in mStormClouds)
            {
                cloud.mDespawn = true;
            }
        }


    }
}
