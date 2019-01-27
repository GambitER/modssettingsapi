﻿package poliroid.gui.lobby.modsSettingsApi.lang
{
	
	public class STRINGS extends Object
	{
		
		public static var WINDOW_TITLE:String = "WINDOW_TITLE";
		public static var BUTTON_APPLY:String = "BUTTON_APPLY";
		public static var BUTTON_OK:String = "BUTTON_OK";
		public static var BUTTON_CANCEL:String = "BUTTON_CLOSE";
		public static var BUTTON_ENABLED_TOOLTIP:String = "BUTTON_ENABLED_TOOLTIP";
		public static var CONTEXT_DEFAULT:String = "CONTEXT_DEFAULT";
		public static var CONTEXT_CLEAN:String = "CONTEXT_CLEAN";
		
		public function STRINGS():void
		{
			super();
		}
		
		public static function setLang(lang:Object):void
		{
			WINDOW_TITLE = lang.WINDOW_TITLE;
			BUTTON_APPLY = lang.BUTTON_APPLY;
			BUTTON_OK = lang.BUTTON_OK;
			BUTTON_CANCEL = lang.BUTTON_CANCEL;
			BUTTON_ENABLED_TOOLTIP = lang.BUTTON_ENABLED_TOOLTIP;
			CONTEXT_DEFAULT = lang.CONTEXT_DEFAULT;
			CONTEXT_CLEAN = lang.CONTEXT_CLEAN;
		}
	}

}