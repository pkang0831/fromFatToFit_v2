-- Atomic credit deduction function to prevent race conditions
CREATE OR REPLACE FUNCTION deduct_user_credits(
  p_user_id UUID,
  p_amount INTEGER
)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
  v_monthly INTEGER;
  v_bonus INTEGER;
  v_remaining INTEGER;
  v_deduct_monthly INTEGER;
  v_deduct_bonus INTEGER;
BEGIN
  -- Lock the row for update to prevent concurrent modifications
  SELECT monthly_credits, bonus_credits
  INTO v_monthly, v_bonus
  FROM user_credits
  WHERE user_id = p_user_id
  FOR UPDATE;
  
  IF NOT FOUND THEN
    RETURN json_build_object('success', false, 'error', 'No credit record found');
  END IF;
  
  -- Check total balance
  IF (v_monthly + v_bonus) < p_amount THEN
    RETURN json_build_object('success', false, 'error', 'Insufficient credits', 'total', v_monthly + v_bonus);
  END IF;
  
  -- Deduct from monthly first, then bonus
  v_remaining := p_amount;
  v_deduct_monthly := LEAST(v_monthly, v_remaining);
  v_remaining := v_remaining - v_deduct_monthly;
  v_deduct_bonus := v_remaining;
  
  UPDATE user_credits
  SET monthly_credits = monthly_credits - v_deduct_monthly,
      bonus_credits = bonus_credits - v_deduct_bonus
  WHERE user_id = p_user_id;
  
  RETURN json_build_object(
    'success', true,
    'monthly_credits', v_monthly - v_deduct_monthly,
    'bonus_credits', v_bonus - v_deduct_bonus,
    'total', (v_monthly - v_deduct_monthly) + (v_bonus - v_deduct_bonus)
  );
END;
$$;
