using System;
using System.Collections;
using System.Collections.Generic;
using System.Dynamic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
using Microsoft.Xna.Framework;

namespace pirates
{
    /// <summary>
    ///  This class implements the basic attributes of every swimming object.
    ///  All moving units will inherit from this abstract class.
    /// </summary>
    abstract class SwimmingObject : IUpdatableObject
    {
        /// <summary>
        /// Boolean, stores information about whether the ship is selected or not. 
        /// </summary>
        private bool Selected { get; set; }

        /// <summary>
        ///  Boolean to check if the ship is owned by the player or not.
        /// </summary>
        private bool Owned { get; set; }

        /// <summary>
        ///  Boolean to set the ship's status to Moving or idling.
        /// </summary>
        private bool Moving { get; set; }

        /// <summary>
        ///  A Vector that represents the position of the ship in the World.
        /// </summary>
        private Vector2 Position { get; set; }

        /// <summary>
        ///  The Vector of the targetposition of the ship.
        /// </summary>
        private Vector2 Target { get; set; }

        /// <summary>
        ///  ArrayList with targets, the complete path of the Ship to its destination.
        /// </summary>
        private ArrayList Path { get; set; }

        /// <summary>
        ///  Integer with the hitpoints of a SwimmingObject
        /// </summary>
        private int Hp { get; set; }

        /// <summary>
        ///  The movementspeed of the ship as a float value, wich will be multiplicated by the 
        ///  direction vector.
        /// </summary>
        private float MovementSpeed { get; set; }

        /// <summary>
        ///  The free pirates to be sent to the stations.
        /// </summary>
        private int FreePirates { get; set; }

        /// <summary>
        /// The Attackvalue for the Canons, is equal to the count of pirates at the canon stations.
        /// </summary>
        private int AttackValue { get; set; }

        /// <summary>
        ///  The number of pirates at the deck, ready to fight when entering a ship.
        /// </summary>
        private int EnterAttackValue { get; set; }

        /// <summary>
        ///  The number of pirates at the repair station.
        /// </summary>
        private int RepairValue { get; set; }

        /// <summary>
        ///  Sets the ship's status to moving and sets the Path ArrayList for the given target Vector. 
        /// <param name="target"> The target of the movement of the ship</param>
        /// </summary>
        public void Move(Vector2 target)
        {
            //call method for Pathfinding
            Path = new ArrayList {new Vector2(2, 3)}; //the return value of the Pathfinding should be stored in Path
            //test only
        }

        /// <summary>
        ///  Update for all Swimming Objects. Contains only Movement and the correspondingly input.
        /// </summary>
        public void Update()
        {
            if (Moving)
            {
               if (Position == Target)
                    {
                        Path.RemoveAt(0);
                        if (Path.Count >= 1)
                        {
                            Target = (Vector2) Path[0];
                        }
                        else
                            Moving = false;
                    }
                    else
                        Position = Position + (Vector2.Normalize(Target - Position) * MovementSpeed); 
            }
            else
            {
                //waiting for input

            }
            
        }

    }

    
}
