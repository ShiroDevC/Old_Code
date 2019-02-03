using System;
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using pirates.AI.Pathfinding;

namespace pirates.GameObjects
{
    class TestShip : AShip, IGameObject, IBattleObject
    {
        public Path mPath = new Path(null);

        public Texture2D ShipSpriteTexture
        {
            get;
            set;
        }

        public void FollowPath(GameTime gameTime)
        {
            if (!mPath.Finished)
            {
                // move to the next grid.
                if (Vector2.Distance(Position, mPath.Next.Cell.Position) > 5)
                {
                    Direction = -(Position - mPath.Next.Cell.Position);
                    Direction.Normalize();

                    Position += (Direction * 25 * (float)gameTime.ElapsedGameTime.TotalSeconds);
                }
                else
                {
                    mPath.GetNextWaypoint();
                }
            }
        }

        public void Attack(Path target)
        {
            throw new NotImplementedException();
        }

        public void Defend(Path target)
        {
            throw new NotImplementedException();
        }

        public void Initialize()
        {
            throw new NotImplementedException();
        }
    }
}