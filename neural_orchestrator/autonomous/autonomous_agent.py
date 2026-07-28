"""
Autonomous Agent - Main Autonomous AI Agent
Coordinates all autonomous components to enable self-steering behavior.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .behavior_predictor import BehaviorPredictor, BehaviorType
from .auto_steerer import AutoSteerer, ActionType
from .api_handler import APIHandler
from .decision_engine import DecisionEngine
from .safety_guardrails import SafetyGuardrails
from ..knowledge_base.user_knowledge_base import UserKnowledgeBase


class AutonomousAgent:
    """
    Main autonomous AI agent that coordinates all autonomous components.
    Enables the system to predict user behavior and steer itself like the user.
    """
    
    def __init__(
        self,
        autonomy_level: float = 0.7,
        risk_tolerance: float = 0.5,
        strict_safety: bool = False
    ):
        """
        Initialize the Autonomous Agent.
        
        Args:
            autonomy_level: Level of autonomy (0-1)
            risk_tolerance: Risk tolerance for decisions (0-1)
            strict_safety: Whether to use strict safety mode
        """
        self.autonomy_level = autonomy_level
        
        # Initialize components
        self.behavior_predictor = BehaviorPredictor(model_complexity=3)
        self.auto_steerer = AutoSteerer(autonomy_level=autonomy_level)
        self.api_handler = APIHandler()
        self.decision_engine = DecisionEngine(risk_tolerance=risk_tolerance)
        self.safety_guardrails = SafetyGuardrails(strict_mode=strict_safety)
        
        # Initialize knowledge base
        self.knowledge_base = UserKnowledgeBase()
        
        # Agent state
        self.is_running = False
        self.current_context: Dict = {}
        self.agent_goals: List[str] = []
        
        # Performance tracking
        self.actions_executed = 0
        self.decisions_made = 0
        self.safety_checks_passed = 0
        self.safety_checks_failed = 0
    
    async def start(self):
        """Start the autonomous agent."""
        self.is_running = True
        print("Autonomous Agent started")
        
        # Start auto steering
        asyncio.create_task(self.auto_steerer.start_steering())
        
        # Main autonomous loop
        while self.is_running:
            await self.autonomous_cycle()
            await asyncio.sleep(1.0)  # Cycle interval
    
    async def stop(self):
        """Stop the autonomous agent."""
        self.is_running = False
        await self.auto_steerer.stop_steering()
        await self.api_handler.close_session()
        print("Autonomous Agent stopped")
    
    async def autonomous_cycle(self):
        """Execute one autonomous cycle."""
        # Update context from current state
        self._update_context()
        
        # Predict next behaviors
        predictions = await self._predict_behaviors()
        
        # Make decisions based on predictions
        decisions = await self._make_decisions(predictions)
        
        # Execute safe decisions
        await self._execute_decisions(decisions)
    
    def _update_context(self):
        """Update current context from various sources."""
        self.current_context = {
            'timestamp': datetime.now().timestamp(),
            'autonomy_level': self.autonomy_level,
            'goals': self.agent_goals,
            'screen': self.auto_steerer.current_context.get('screen', 'unknown')
        }
    
    async def _predict_behaviors(self) -> List[Dict]:
        """
        Predict next user behaviors.
        
        Returns:
            List of behavior predictions
        """
        predictions = []
        
        # Predict for each behavior type
        for behavior_type in BehaviorType:
            prediction = self.behavior_predictor.predict_next_behavior(
                behavior_type=behavior_type,
                context=self.current_context
            )
            predictions.append({
                'behavior_type': behavior_type.value,
                'predicted_action': prediction.predicted_action,
                'confidence': prediction.confidence,
                'context': prediction.context
            })
        
        return predictions
    
    async def _make_decisions(self, predictions: List[Dict]) -> List[Dict]:
        """
        Make decisions based on predictions.
        
        Args:
            predictions: Behavior predictions
            
        Returns:
            List of decisions made
        """
        decisions = []
        
        # Get available actions based on predictions
        available_actions = self._generate_available_actions(predictions)
        
        # Make decision for each high-confidence prediction
        for prediction in predictions:
            if prediction['confidence'] > 0.6:  # Only act on confident predictions
                decision = self.decision_engine.make_decision(
                    prediction=prediction,
                    context=self.current_context,
                    available_actions=available_actions
                )
                decisions.append({
                    'decision_id': decision.decision_id,
                    'action': decision.action,
                    'parameters': decision.parameters,
                    'confidence': decision.confidence,
                    'priority': decision.priority.name,
                    'reasoning': decision.reasoning
                })
                self.decisions_made += 1
        
        return decisions
    
    def _generate_available_actions(self, predictions: List[Dict]) -> List[Dict]:
        """
        Generate available actions based on predictions.
        
        Args:
            predictions: Behavior predictions
            
        Returns:
            List of available actions
        """
        actions = []
        
        for prediction in predictions:
            predicted_action = prediction['predicted_action']
            
            # Map predicted actions to executable actions
            if 'click' in predicted_action or 'tap' in predicted_action:
                actions.append({
                    'action': 'click',
                    'parameters': {
                        'x': 0.5,
                        'y': 0.5,
                        'element_id': predicted_action
                    }
                })
            elif 'scroll' in predicted_action:
                direction = predicted_action.split('_')[-1] if '_' in predicted_action else 'down'
                actions.append({
                    'action': 'scroll',
                    'parameters': {
                        'direction': direction,
                        'amount': 100
                    }
                })
            elif 'navigate' in predicted_action:
                actions.append({
                    'action': 'navigate',
                    'parameters': {
                        'target_screen': 'next',
                        'method': 'tap'
                    }
                })
        
        return actions
    
    async def _execute_decisions(self, decisions: List[Dict]):
        """
        Execute decisions after safety checks.
        
        Args:
            decisions: Decisions to execute
        """
        for decision in decisions:
            # Safety check
            safety_check = self.safety_guardrails.check_action_safety(
                action=decision['action'],
                parameters=decision['parameters'],
                context=self.current_context
            )
            
            if safety_check.approved:
                # Queue action for execution
                action_type = self._map_to_action_type(decision['action'])
                self.auto_steerer.queue_action(
                    action_type=action_type,
                    parameters=decision['parameters'],
                    confidence=decision['confidence']
                )
                self.actions_executed += 1
                self.safety_checks_passed += 1
            else:
                self.safety_checks_failed += 1
                print(f"Action blocked by safety guardrails: {safety_check.reasoning}")
    
    def _map_to_action_type(self, action: str) -> ActionType:
        """Map action string to ActionType enum."""
        action_mapping = {
            'click': ActionType.CLICK,
            'scroll': ActionType.SCROLL,
            'type': ActionType.TYPE,
            'navigate': ActionType.NAVIGATE,
            'swipe': ActionType.SWIPE,
            'wait': ActionType.WAIT,
            'api_call': ActionType.API_CALL
        }
        return action_mapping.get(action, ActionType.WAIT)
    
    def record_user_behavior(self, behavior_type: str, action_data: Dict, context: Optional[Dict] = None):
        """
        Record observed user behavior for learning.
        
        Args:
            behavior_type: Type of behavior
            action_data: Action data
            context: Context information
        """
        try:
            behavior_enum = BehaviorType(behavior_type)
            self.behavior_predictor.record_behavior(
                behavior_type=behavior_enum,
                action_data=action_data,
                context=context
            )
            
            # Also add to knowledge base as experience
            self.knowledge_base.add_experience(
                experience_data=action_data,
                experience_type=behavior_type,
                metadata=context or {}
            )
        except ValueError:
            print(f"Unknown behavior type: {behavior_type}")
    
    def set_goals(self, goals: List[str]):
        """
        Set autonomous agent goals.
        
        Args:
            goals: List of goal descriptions
        """
        self.agent_goals = goals
        self.decision_engine.set_goals(goals)
    
    def set_autonomy_level(self, level: float):
        """
        Set autonomy level.
        
        Args:
            level: New autonomy level (0-1)
        """
        self.autonomy_level = min(max(level, 0.0), 1.0)
        self.auto_steerer.adjust_autonomy_level(level)
    
    def get_agent_status(self) -> Dict:
        """
        Get current agent status.
        
        Returns:
            Dictionary containing agent status
        """
        return {
            'is_running': self.is_running,
            'autonomy_level': self.autonomy_level,
            'current_goals': self.agent_goals,
            'actions_executed': self.actions_executed,
            'decisions_made': self.decisions_made,
            'safety_checks_passed': self.safety_checks_passed,
            'safety_checks_failed': self.safety_checks_failed,
            'behavior_statistics': self.behavior_predictor.get_behavior_statistics(),
            'steering_statistics': self.auto_steerer.get_steering_statistics(),
            'decision_statistics': self.decision_engine.get_decision_statistics(),
            'safety_statistics': self.safety_guardrails.get_safety_statistics(),
            'knowledge_base_status': self.knowledge_base.get_comprehensive_status()
        }
    
    def configure_api(self, base_url: str, auth_token: Optional[str] = None, api_key: Optional[str] = None):
        """
        Configure API handler.
        
        Args:
            base_url: Base URL for API requests
            auth_token: Authentication token
            api_key: API key
        """
        self.api_handler.base_url = base_url
        if auth_token:
            self.api_handler.set_auth_token(auth_token)
        if api_key:
            self.api_handler.set_api_key(api_key)
