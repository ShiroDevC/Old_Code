using System.Collections.Generic;
using Microsoft.Xna.Framework;

namespace pirates.GameObjects
{
    public sealed class QuadTree
    {
        private const int MaxObjects = 10;
        private const int MaxLevels = 5;
        private readonly int mLevel;
        private readonly List<AShip> mObjects;
        private Rectangle mBounds;
        private readonly QuadTree[] mNodes;

        public QuadTree(int pLevel, Rectangle pBounds)
        {
            mLevel = pLevel;
            mObjects = new List<AShip>();
            mBounds = pBounds;
            mNodes = new QuadTree[4];
        }

        /// <summary>
        /// Clears the QuadTree.
        /// </summary>
        public void Clear()
        {
            mObjects.Clear();

            for (var i = 0; i < mNodes.Length; i++)
            {
                if (mNodes[i] == null) continue;
                mNodes[i].Clear();
                mNodes[i] = null;
            }

        }

        /// <summary>
        /// Splits a Quad into 4 Subquads.
        /// </summary>
        private void Split()
        {
            var subWidth =(mBounds.Width / 2);
            var subHeight = (mBounds.Height / 2);
            var x = mBounds.X;
            var y = mBounds.Y;

            mNodes[0] = new QuadTree(mLevel + 1, new Rectangle(x + subWidth, y, subWidth, subHeight));
            mNodes[1] = new QuadTree(mLevel + 1, new Rectangle(x, y, subWidth, subHeight));
            mNodes[2] = new QuadTree(mLevel + 1, new Rectangle(x, y + subHeight, subWidth, subHeight));
            mNodes[3] = new QuadTree(mLevel + 1, new Rectangle(x + subWidth, y + subHeight, subWidth, subHeight));
        }

        /// <summary>
        /// Returns the index of the node, where the Ship is. -1 if its between 2 nodes.
        /// </summary>
        private int GetIndex(AShip ship)
        {
            int index = -1;
            double verticalMidpoint = mBounds.X + (mBounds.Width / 2);
            double horizontalMidpoint = mBounds.Y + (mBounds.Height / 2);

            // Object can completely fit within the top quadrants
            bool topQuadrant = (ship.Position.Y < horizontalMidpoint && ship.Position.Y + ship.mShipTexture.Height  < horizontalMidpoint);
            // Object can completely fit within the bottom quadrants
            bool bottomQuadrant = (ship.Position.Y > horizontalMidpoint);

            // Object can completely fit within the left quadrants
            if (ship.Position.X < verticalMidpoint && ship.Position.X + ship.mShipTexture.Width < verticalMidpoint)
            {
                if (topQuadrant)
                {
                    index = 1;
                }
                else if (bottomQuadrant)
                {
                    index = 2;
                }
            }
            // Object can completely fit within the right quadrants
            else if (ship.Position.X > verticalMidpoint)
            {
                if (topQuadrant)
                {
                    index = 0;
                }
                else if (bottomQuadrant)
                {
                    index = 3;
                }
            }

            return index;
        }

        /// <summary>
        /// Inserts the object to the correct Node.
        /// </summary>
        public void Insert(AShip ship)
        {
            if (mNodes[0] != null)
            {
                var index = GetIndex(ship);

                if (index != -1)
                {
                    mNodes[index].Insert(ship);

                    return;
                }
            }

            mObjects.Add(ship);

            if (mObjects.Count > MaxObjects && mLevel < MaxLevels)
            {
                if (mNodes[0] == null)
                {
                    Split();
                }

                var i = 0;
                while (i < mObjects.Count)
                {
                    var index = GetIndex(mObjects[i]);
                    if (index != -1)
                    {
                        mNodes[index].Insert(mObjects[i]);
                        mObjects.RemoveAt(i);
                    }
                    else
                    {
                        i++;
                    }
                }
            }
        }


        // ReSharper disable once UnusedMethodReturnValue.Global
        public List<AShip> Retrieve(List<AShip> returnObjects, AShip ship)
        {
            var index = GetIndex(ship);
            if (index != -1 && mNodes[0] != null)
            {
                mNodes[index].Retrieve(returnObjects, ship);
            }
            returnObjects.AddRange(mObjects);

            return returnObjects;
        }

    }
}
